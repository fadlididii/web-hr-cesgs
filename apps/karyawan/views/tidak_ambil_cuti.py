from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.hrd.models import TidakAmbilCuti, Karyawan, CutiBersama
from apps.karyawan.forms import TidakAmbilCutiForm
from datetime import datetime
from django.db.models import Q

@login_required
def tidak_ambil_cuti_view(request):
    karyawan = get_object_or_404(Karyawan, user=request.user)

    # Ambil semua tanggal cuti bersama
    semua_cuti_bersama = CutiBersama.objects.all()

    # Ambil tanggal yang sudah diajukan dan disetujui
    pengajuan_disetujui = TidakAmbilCuti.objects.filter(
        id_karyawan=karyawan,
        status='disetujui'
    ).values_list('tanggal__id', flat=True)

    # Filter daftar tanggal cuti bersama yang belum diajukan
    sisa_tanggal = semua_cuti_bersama.exclude(id__in=pengajuan_disetujui)

    # Form khusus untuk pilihan tanggal
    if request.method == 'POST':
        form = TidakAmbilCutiForm(request.POST, request.FILES)
        form.fields['tanggal'].queryset = sisa_tanggal  # inject pilihan yang belum diajukan
        if form.is_valid():
            tidak_ambil = form.save(commit=False)
            tidak_ambil.id_karyawan = karyawan
            tidak_ambil.save()
            form.save_m2m()
            messages.success(request, "Pengajuan berhasil dikirim.")
            return redirect('tidak_ambil_cuti')
    else:
        form = TidakAmbilCutiForm()
        form.fields['tanggal'].queryset = sisa_tanggal

    riwayat = TidakAmbilCuti.objects.filter(id_karyawan=karyawan).order_by('-tanggal_pengajuan')
    return render(request, 'karyawan/tidak_ambil_cuti.html', {
        'form': form,
        'riwayat': riwayat,
    })

@login_required
def hapus_tidak_ambil_cuti_view(request, id):
    karyawan = get_object_or_404(Karyawan, user=request.user)
    pengajuan = get_object_or_404(TidakAmbilCuti, id=id, id_karyawan=karyawan)

    if pengajuan.status == 'menunggu':
        pengajuan.delete()
        messages.success(request, "Pengajuan berhasil dihapus.")
    else:
        messages.warning(request, "Pengajuan yang sudah diproses tidak dapat dihapus.")

    return redirect('tidak_ambil_cuti')
