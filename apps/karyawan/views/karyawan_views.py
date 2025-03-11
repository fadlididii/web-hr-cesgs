from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.authentication.decorators import role_required

@login_required
@role_required(['Karyawan Tetap'])
def karyawan_dashboard(request):
    return render(request, 'karyawan/index.html')

@login_required
@role_required(['Karyawan Tetap'])
def pengajuan_cuti(request):
    return render(request, 'karyawan/pengajuan_cuti.html')

@login_required
@role_required(['Karyawan Tetap'])
def pengajuan_izin(request):
    return render(request, 'karyawan/pengajuan_izin.html')

@login_required
@role_required(['Karyawan Tetap'])
def edit_profil(request):
    return render(request, 'karyawan/edit_profil.html')
