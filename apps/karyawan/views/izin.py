from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.hrd.models import Izin, Karyawan
from apps.hrd.forms import IzinForm

@login_required
def izin_view(request):
    karyawan = get_object_or_404(Karyawan, user=request.user)
    if request.method == 'POST':
        form = IzinForm(request.POST, request.FILES)
        if form.is_valid():
            izin = form.save(commit=False)
            izin.id_karyawan = karyawan
            izin.save()
            messages.success(request, "Pengajuan izin berhasil dikirim.")
            return redirect('pengajuan_izin')
    else:
        form = IzinForm()
    riwayat = Izin.objects.filter(id_karyawan=karyawan).order_by('-tanggal_pengajuan')
    return render(request, 'karyawan/form_dan_riwayat_izin.html', {'form': form, 'riwayat': riwayat})

@login_required
def hapus_izin_view(request, id):
    karyawan = get_object_or_404(Karyawan, user=request.user)
    izin = get_object_or_404(Izin, id=id, id_karyawan=karyawan)

    if izin.status == 'menunggu':
        izin.delete()
        messages.success(request, "Pengajuan izin berhasil dihapus.")
    else:
        messages.warning(request, "Pengajuan yang sudah diproses tidak dapat dihapus.")

    return redirect('pengajuan_izin')
