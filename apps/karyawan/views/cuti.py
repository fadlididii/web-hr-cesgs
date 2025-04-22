from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.hrd.models import Cuti, Karyawan
from apps.hrd.forms import CutiForm

@login_required
def cuti_view(request):
    karyawan = get_object_or_404(Karyawan, user=request.user)

    # ✅ Batasi hanya untuk HRD & Karyawan Tetap
    if karyawan.user.role not in ['HRD', 'Karyawan Tetap']:
        messages.error(request, "Anda tidak memiliki akses ke fitur pengajuan cuti.")
        return redirect('karyawan_dashboard')

    if request.method == 'POST':
        form = CutiForm(request.POST, request.FILES)
        if form.is_valid():
            cuti = form.save(commit=False)
            cuti.id_karyawan = karyawan
            cuti.save()
            messages.success(request, "Pengajuan cuti berhasil dikirim.")
            return redirect('pengajuan_cuti')
    else:
        form = CutiForm()

    riwayat = Cuti.objects.filter(id_karyawan=karyawan).order_by('-tanggal_pengajuan')

    return render(request, 'karyawan/pengajuan_dan_riwayat_cuti.html', {
        'form': form,
        'riwayat': riwayat
    })


@login_required
def hapus_cuti_view(request, id):
    karyawan = get_object_or_404(Karyawan, user=request.user)

    # ✅ Batasi hanya role yang diizinkan menghapus
    if karyawan.user.role not in ['HRD', 'Karyawan Tetap']:
        messages.error(request, "Anda tidak memiliki akses untuk menghapus pengajuan cuti.")
        return redirect('pengajuan_cuti')

    cuti = get_object_or_404(Cuti, id=id, id_karyawan=karyawan)

    if cuti.status == 'menunggu':
        cuti.delete()
        messages.success(request, "Pengajuan cuti berhasil dihapus.")
    else:
        messages.warning(request, "Pengajuan yang sudah diproses tidak dapat dihapus.")

    return redirect('pengajuan_cuti')
