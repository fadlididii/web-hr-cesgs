from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.authentication.decorators import role_required
from django.contrib import messages
from apps.absensi.forms import UploadAbsensiForm
from apps.absensi.models import Absensi
from apps.absensi.utils import process_absensi
from datetime import datetime
import openpyxl
from django.db.models import Max
from django.http import HttpResponse
from django.conf import settings
import os

@login_required
@role_required(['HRD'])
def upload_absensi(request):
    # Ambil bulan dan tahun dari query string
    try:
        bulan = int(request.GET.get('bulan', datetime.now().month))
        tahun = int(request.GET.get('tahun', datetime.now().year))
    except ValueError:
        bulan, tahun = datetime.now().month, datetime.now().year

    query = request.GET.get('q', '')

    # 🔎 Filter absensi
    absensi_list = Absensi.objects.filter(bulan=bulan, tahun=tahun)
    if query:
        absensi_list = absensi_list.filter(id_karyawan__nama__icontains=query)
    absensi_list = absensi_list.order_by('tanggal', 'id_karyawan_id')

    # 🔁 Paginate
    paginator = Paginator(absensi_list, 10)
    page = request.GET.get('page')
    try:
        absensi_list = paginator.page(page)
    except PageNotAnInteger:
        absensi_list = paginator.page(1)
    except EmptyPage:
        absensi_list = paginator.page(paginator.num_pages)

    # ✅ Upload file
    if request.method == 'POST':
        form = UploadAbsensiForm(request.POST, request.FILES)
        if form.is_valid():
            bulan = int(form.cleaned_data['bulan'])
            tahun = int(form.cleaned_data['tahun'])
            file = form.cleaned_data['file']
            selected_rule = form.cleaned_data['rules']

            # Simpan file ke /media/absensi/
            relative_path = f"absensi/{file.name}"
            file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Proses dan simpan ke DB
            file_url = f"{settings.MEDIA_URL}{relative_path}"
            process_absensi(
                file_path=file_path,
                bulan=bulan,
                tahun=tahun,
                selected_rule=selected_rule,
                file_name=file.name,
                file_url=file_url
            )

            messages.success(request, 'Data absensi berhasil diproses!')
            return redirect('upload_absensi')
        else:
            messages.error(request, '⚠ Terjadi kesalahan dalam mengupload file.')
    else:
        form = UploadAbsensiForm()

    # 🔁 Ambil file yang sudah pernah diunggah (distinct by file name)
    uploaded_files = (
        Absensi.objects
        .values('bulan', 'tahun', 'nama_file', 'file_url')
        .annotate(created_at=Max('created_at'))
        .order_by('-created_at')
    )

    context = {
        'form': form,
        'absensi_list': absensi_list,
        'uploaded_files': uploaded_files,
        'selected_bulan': bulan,
        'selected_tahun': tahun,
        'bulan_choices': [(i, datetime(2024, i, 1).strftime('%B')) for i in range(1, 13)],
        'tahun_choices': range(2020, 2031),
        'query': query,
    }
    return render(request, 'absensi/upload_absensi.html', context)


# ✅ 2️⃣ Menghapus satu data absensi
@login_required
@role_required(['HRD'])
def delete_absensi(request, id):
    """Menghapus satu data absensi berdasarkan ID"""
    absensi = get_object_or_404(Absensi, id_absensi=id)
    absensi.delete()
    messages.success(request, "Data absensi berhasil dihapus.")
    return redirect("upload_absensi")


# ✅ 3️⃣ Menghapus semua data absensi dalam bulan & tahun tertentu
@login_required
@role_required(['HRD'])
def hapus_absensi_bulanan(request):
    """Menghapus seluruh data absensi dalam bulan & tahun tertentu"""
    if request.method == "POST":
        bulan = request.POST.get("bulan")
        tahun = request.POST.get("tahun")

        if not bulan or not tahun:
            messages.error(request, "Pilih bulan dan tahun yang ingin dihapus.")
            return redirect("upload_absensi")

        # Hapus semua data absensi berdasarkan bulan dan tahun
        deleted_count, _ = Absensi.objects.filter(bulan=int(bulan), tahun=int(tahun)).delete()

        if deleted_count > 0:
            messages.success(request, f"Berhasil menghapus {deleted_count} data absensi untuk bulan {bulan}-{tahun}.")
        else:
            messages.warning(request, "⚠ Tidak ada data yang ditemukan untuk bulan ini.")

    return redirect("upload_absensi")

@login_required
@role_required(['HRD'])
def export_absensi_excel(request):
    bulan = request.GET.get("bulan")
    tahun = request.GET.get("tahun")
    q = request.GET.get("q", "")

    absensi = Absensi.objects.filter(bulan=bulan, tahun=tahun)
    if q:
        absensi = absensi.filter(id_karyawan__nama__icontains=q)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rekap Absensi"

    ws.append(["Nama", "Tanggal", "Jam Masuk", "Jam Keluar", "Status"])

    for a in absensi.order_by("tanggal", "id_karyawan__nama"):
        ws.append([
            a.id_karyawan.nama,
            a.tanggal.strftime("%Y-%m-%d"),
            a.jam_masuk.strftime("%H:%M") if a.jam_masuk else "-",
            a.jam_keluar.strftime("%H:%M") if a.jam_keluar else "-",
            a.status_absensi,
        ])

    filename = f"rekap_absensi_{bulan}_{tahun}.xlsx"
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response