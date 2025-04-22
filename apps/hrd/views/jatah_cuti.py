from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.hrd.models import JatahCuti
from django.db.models import Q

@login_required
def lihat_jatah_cuti_view(request):
    if request.user.role != 'HRD':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect('karyawan_dashboard')

    tahun = request.GET.get('tahun')
    nama = request.GET.get('nama')

    queryset = JatahCuti.objects.select_related('karyawan')

    if tahun:
        queryset = queryset.filter(tahun=tahun)

    if nama:
        queryset = queryset.filter(karyawan__nama__icontains=nama)

    data = queryset.order_by('tahun', 'karyawan__nama')

    return render(request, 'hrd/jatah_cuti.html', {
        'data': data,
        'filter_tahun': tahun,
        'filter_nama': nama,
    })
