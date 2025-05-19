from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from datetime import datetime, timedelta
from collections import defaultdict
from calendar import month_name
from pytanggalmerah import TanggalMerah
from django.http import JsonResponse

from apps.absensi.models import Absensi
from apps.hrd.models import Cuti, Izin, JatahCuti, CutiBersama


@login_required
def karyawan_dashboard(request):
    user = request.user
    karyawan = user.karyawan  

    today = datetime.today()
    tahun = int(request.GET.get("tahun", today.year))
    bulan = int(request.GET.get("bulan", today.month))
    
    bulan_choices = [(i, month_name[i]) for i in range(1, 13)]
    tahun_choices = list(range(datetime.now().year - 2, datetime.now().year + 3))

    # --- Statistik Pribadi ---
    total_pengajuan_cuti = Cuti.objects.filter(id_karyawan=karyawan).count()
    total_pengajuan_izin = Izin.objects.filter(id_karyawan=karyawan).count()
    jatah = JatahCuti.objects.filter(karyawan=karyawan, tahun=datetime.now().year).first()
    sisa_cuti = jatah.sisa_cuti if jatah else 0

    # --- Hari Kerja Bulan Ini (Senin–Jumat) ---
    total_hari = (datetime(tahun, bulan + 1, 1) - timedelta(days=1)).day if bulan != 12 else 31
    hari_kerja = sum(
        1 for day in range(1, total_hari + 1)
        if datetime(tahun, bulan, day).weekday() < 5
    )

    # Top 5 Karyawan Terlambat (seluruh kantor)
    top_terlambat_qs = (
        Absensi.objects
        .filter(status_absensi="Terlambat", bulan=bulan, tahun=tahun)
        .values("id_karyawan__nama")
        .annotate(total_terlambat=Count("id_karyawan"))
        .order_by("-total_terlambat")[:5]
    )

    top_terlambat_labels = [x["id_karyawan__nama"] for x in top_terlambat_qs]
    top_terlambat_data = [x["total_terlambat"] for x in top_terlambat_qs]

    # Top 5 Karyawan Tepat Waktu (seluruh kantor)
    top_tepat_qs = (
        Absensi.objects
        .filter(status_absensi="Tepat Waktu", bulan=bulan, tahun=tahun)
        .values("id_karyawan__nama")
        .annotate(total_tepat=Count("id_karyawan"))
        .order_by("-total_tepat")[:5]
    )

    top_tepat_labels = [x["id_karyawan__nama"] for x in top_tepat_qs]
    top_tepat_data = [x["total_tepat"] for x in top_tepat_qs]


    # --- Libur Nasional Terdekat (30 hari ke depan) ---
    libur_terdekat = []
    tanggal_mulai = today.date()
    tanggal_sampai = tanggal_mulai + timedelta(days=30)

    for hari in range((tanggal_sampai - tanggal_mulai).days):
        tanggal = tanggal_mulai + timedelta(days=hari)
        t = TanggalMerah()
        t.set_date(str(tanggal.year), f"{tanggal.month:02d}", f"{tanggal.day:02d}")
        if t.check():
            for event in t.get_event():
                libur_terdekat.append({
                    "summary": event,
                    "date": tanggal
                })

    context = {
        "sisa_cuti": sisa_cuti,
        "total_pengajuan_cuti": total_pengajuan_cuti,
        "total_pengajuan_izin": total_pengajuan_izin,
        "hari_kerja": hari_kerja,
        "top_terlambat_labels": top_terlambat_labels,
        "top_terlambat_data": top_terlambat_data,
        "top_tepat_labels": top_tepat_labels,
        "top_tepat_data": top_tepat_data,
        "libur_terdekat": libur_terdekat,
        "bulan_choices": bulan_choices,
        "tahun_choices": tahun_choices,
        "selected_bulan": str(bulan),
        "selected_tahun": str(tahun),
    }

    return render(request, "karyawan/index.html", context)

@login_required
def calendar_events(request):
    events = []

    # Gabungkan cuti berdasarkan tanggal
    grouped_cuti = defaultdict(list)
    for c in Cuti.objects.filter(status='disetujui'):
        current_date = c.tanggal_mulai
        while current_date <= c.tanggal_selesai:
            grouped_cuti[current_date].append(c.id_karyawan.nama)
            current_date += timedelta(days=1)

    for date, names in grouped_cuti.items():
        events.append({
            "title": f"Cuti ({len(names)} orang)",
            "start": date.isoformat(),
            "color": "#f5365c",
            "description": ", ".join(names)  # untuk custom tooltip
        })

    # Izin
    grouped_izin = defaultdict(list)
    for i in Izin.objects.filter(status='disetujui'):
        grouped_izin[i.tanggal_izin].append(i.id_karyawan.nama)

    for date, names in grouped_izin.items():
        events.append({
            "title": f"Izin ({len(names)} orang)",
            "start": date.isoformat(),
            "color": "#11cdef",
            "description": ", ".join(names)
        })

    # Tanggal Merah
    today = datetime.now().date()
    end_date = today + timedelta(days=365)
    current_date = today
    
    while current_date <= end_date:
        t = TanggalMerah()
        t.set_date(str(current_date.year), f"{current_date.month:02d}", f"{current_date.day:02d}")
        if t.check():
            for event in t.get_event():
                events.append({
                    "title": event,
                    "start": current_date.isoformat(),
                    "color": "#fb6340",
                    "allDay": True
                })
        current_date += timedelta(days=1)

    # Cuti Bersama
    for cb in CutiBersama.objects.all():
        events.append({
            "title": f"Cuti Bersama: {cb.keterangan or 'Cuti Bersama'}",
            "start": cb.tanggal.isoformat(),
            "color": "#5e72e4",
            "allDay": True
        })

    # Add a debug event if no events are found
    if not events:
        events.append({
            "title": "Debug Event",
            "start": today.isoformat(),
            "color": "#cccccc",
            "allDay": True
        })

    return JsonResponse(events, safe=False)

@login_required
def data_dashboard_karyawan(request):
    user = request.user
    karyawan = user.karyawan

    bulan = int(request.GET.get("bulan", datetime.now().month))
    tahun = int(request.GET.get("tahun", datetime.now().year))

    # hitung semua data yang sama seperti view utama
    total_pengajuan_cuti = Cuti.objects.filter(id_karyawan=karyawan, tanggal_mulai__year=tahun, tanggal_mulai__month=bulan).count()
    total_pengajuan_izin = Izin.objects.filter(id_karyawan=karyawan, tanggal_izin__year=tahun, tanggal_izin__month=bulan).count()

    jatah = JatahCuti.objects.filter(karyawan=karyawan, tahun=tahun).first()
    sisa_cuti = jatah.sisa_cuti if jatah else 0

    # top terlambat (seluruh kantor)
    top_terlambat_qs = (
        Absensi.objects
        .filter(status_absensi="Terlambat", bulan=bulan, tahun=tahun)
        .values("id_karyawan__nama")
        .annotate(jumlah=Count("id_karyawan"))
        .order_by("-jumlah")[:5]
    )
    top_terlambat_labels = [x["id_karyawan__nama"] for x in top_terlambat_qs]
    top_terlambat_data = [x["jumlah"] for x in top_terlambat_qs]

    # top tepat waktu (seluruh kantor)
    top_tepat_qs = (
        Absensi.objects
        .filter(status_absensi="Tepat Waktu", bulan=bulan, tahun=tahun)
        .values("id_karyawan__nama")
        .annotate(jumlah=Count("id_karyawan"))
        .order_by("-jumlah")[:5]
    )
    top_tepat_labels = [x["id_karyawan__nama"] for x in top_tepat_qs]
    top_tepat_data = [x["jumlah"] for x in top_tepat_qs]

    return JsonResponse({
        "sisa_cuti": sisa_cuti,
        "total_pengajuan_cuti": total_pengajuan_cuti,
        "total_pengajuan_izin": total_pengajuan_izin,
        "top_terlambat_labels": top_terlambat_labels,
        "top_terlambat_data": top_terlambat_data,
        "top_tepat_labels": top_tepat_labels,
        "top_tepat_data": top_tepat_data,
    })