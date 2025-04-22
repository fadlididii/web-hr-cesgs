from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from apps.hrd.models import Cuti, TidakAmbilCuti, JatahCuti
from apps.authentication.models import User
from django.db.models import Q
import openpyxl

@login_required
def approval_cuti_view(request):
    if request.user.role != 'HRD':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect('karyawan_dashboard')

    daftar_cuti = Cuti.objects.filter(status='menunggu').order_by('-tanggal_pengajuan')
    daftar_tidak_ambil = TidakAmbilCuti.objects.filter(status='menunggu').order_by('-tanggal_pengajuan')
    riwayat_cuti = Cuti.objects.exclude(status='menunggu').order_by('-tanggal_pengajuan')

    if request.method == 'POST':
        jenis = request.POST.get('jenis')
        aksi = request.POST.get('aksi')
        alasan_ditolak = request.POST.get('alasan_ditolak', '')

        if jenis == 'cuti':
            cuti_id = request.POST.get('cuti_id')
            cuti = get_object_or_404(Cuti, id=cuti_id)

            if aksi in ['disetujui', 'ditolak']:
                cuti.status = aksi
                cuti.approval = request.user

                if aksi == 'ditolak':
                    cuti.alasan_ditolak = alasan_ditolak

                file_persetujuan = request.FILES.get('file_persetujuan')
                if file_persetujuan:
                    cuti.file_persetujuan = file_persetujuan

                if aksi == 'disetujui' and cuti.jenis_cuti == 'tahunan':
                    tahun = cuti.tanggal_mulai.year
                    jumlah_hari = (cuti.tanggal_selesai - cuti.tanggal_mulai).days + 1

                    if cuti.id_karyawan.user.role in ['HRD', 'Karyawan Tetap']:
                        jatah, _ = JatahCuti.objects.get_or_create(
                            karyawan=cuti.id_karyawan, tahun=tahun,
                            defaults={'total_cuti': 12, 'sisa_cuti': 12}
                        )
                        jatah.sisa_cuti -= jumlah_hari
                        jatah.save()

                cuti.save()
                messages.success(request, f"Pengajuan cuti berhasil {aksi}.")

        elif jenis == 'tidak_ambil':
            tidak_ambil_id = request.POST.get('tidak_ambil_id')
            data = get_object_or_404(TidakAmbilCuti, id=tidak_ambil_id)

            if aksi in ['disetujui', 'ditolak']:
                data.status = aksi
                data.approval = request.user

                if aksi == 'ditolak':
                    data.alasan_ditolak = alasan_ditolak

                file_persetujuan = request.FILES.get('file_persetujuan')
                if file_persetujuan:
                    data.file_persetujuan = file_persetujuan

                if aksi == 'disetujui':
                    daftar_tanggal = data.tanggal.all()
                    jumlah_tanggal = daftar_tanggal.count()

                    if jumlah_tanggal > 0:
                        tahun = daftar_tanggal.first().tanggal.year

                        if data.id_karyawan.user.role in ['HRD', 'Karyawan Tetap']:
                            jatah, _ = JatahCuti.objects.get_or_create(
                                karyawan=data.id_karyawan, tahun=tahun,
                                defaults={'total_cuti': 12, 'sisa_cuti': 12}
                            )
                            jatah.sisa_cuti += jumlah_tanggal
                            jatah.save()

                data.save()
                messages.success(request, f"Pengajuan tidak ambil cuti berhasil {aksi}.")

        return redirect('approval_cuti')

    # Filter riwayat
    riwayat_cuti = Cuti.objects.exclude(status='menunggu')
    keyword = request.GET.get('nama')
    tahun = request.GET.get('tahun')

    if keyword:
        riwayat_cuti = riwayat_cuti.filter(id_karyawan__nama__icontains=keyword)
    if tahun:
        riwayat_cuti = riwayat_cuti.filter(tanggal_mulai__year=tahun)

    riwayat_cuti = riwayat_cuti.order_by('-tanggal_pengajuan')

    return render(request, 'hrd/approval_cuti.html', {
        'daftar_cuti': daftar_cuti,
        'daftar_tidak_ambil': daftar_tidak_ambil,
        'riwayat_cuti': riwayat_cuti,
    })


@login_required
def export_riwayat_cuti_excel(request):
    if request.user.role != 'HRD':
        return HttpResponse("Forbidden", status=403)

    riwayat = Cuti.objects.exclude(status='menunggu').order_by('-tanggal_pengajuan')

    keyword = request.GET.get('nama')
    tahun = request.GET.get('tahun')

    if keyword:
        riwayat = riwayat.filter(id_karyawan__nama__icontains=keyword)
    if tahun:
        riwayat = riwayat.filter(tanggal_mulai__year=tahun)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Riwayat Cuti"

    ws.append(["Nama", "Jenis Cuti", "Tanggal Mulai", "Tanggal Selesai", "Status", "Disetujui Oleh"])

    for r in riwayat:
        ws.append([
            r.id_karyawan.nama,
            r.get_jenis_cuti_display(),
            r.tanggal_mulai.strftime('%Y-%m-%d'),
            r.tanggal_selesai.strftime('%Y-%m-%d'),
            r.status,
            r.approval.get_full_name() if r.approval else '-'
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=riwayat_cuti.xlsx'
    wb.save(response)
    return response
