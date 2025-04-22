from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from apps.authentication.decorators import role_required
from apps.absensi.models import Absensi
from datetime import datetime

@login_required
@role_required(['HRD'])
def hrd_dashboard(request):
    print(f"✅ REQUEST GET DATA: {request.GET}")  # Debugging

    # Ambil bulan dan tahun dari request GET
    bulan = request.GET.get("bulan", str(datetime.now().month))
    tahun = request.GET.get("tahun", str(datetime.now().year))

    # 🔹 Perbaiki format tahun yang salah
    if isinstance(tahun, str) and tahun.startswith("("):
        tahun = tahun.strip("()").replace("'", "").split(",")[0].strip()

    # Konversi ke integer dengan pengecekan error
    try:
        bulan = int(bulan)
        tahun = int(tahun)
    except ValueError:
        bulan = datetime.now().month
        tahun = datetime.now().year

    print(f"🔍 Filter Data: Bulan={bulan}, Tahun={tahun}")  # Debugging

    # Query data top 5 karyawan paling sering terlambat
    top_5_late = (
        Absensi.objects.filter(status_absensi="Terlambat", bulan=bulan, tahun=tahun)
        .values("id_karyawan__nama")
        .annotate(total_terlambat=Count("id_karyawan"))
        .order_by("-total_terlambat")[:5]
    )

    print(f"📊 Data Karyawan Terlambat: {list(top_5_late)}")  # Debugging

    bulan_choices = [(str(i), datetime(2000, i, 1).strftime("%B")) for i in range(1, 13)]
    tahun_choices = [(str(i), str(i)) for i in range(2020, 2031)]

    context = {
        "top_5_late": top_5_late,
        "bulan_choices": bulan_choices,
        "tahun_choices": tahun_choices,
        "selected_bulan": str(bulan),
        "selected_tahun": str(tahun),
    }
    return render(request, "hrd/index.html", context)
