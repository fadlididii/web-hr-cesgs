from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.hrd.models import Cuti, Karyawan, JatahCuti
from apps.karyawan.forms import CutiForm
from datetime import datetime
from notifications.signals import notify
from apps.authentication.models import User

@login_required
def cuti_view(request):
    karyawan = get_object_or_404(Karyawan, user=request.user)

    #  Batasi hanya untuk HRD & Karyawan Tetap
    if karyawan.user.role not in ['HRD', 'Karyawan Tetap']:
        messages.error(request, "Anda tidak memiliki akses ke fitur pengajuan cuti.")
        return redirect('karyawan_dashboard')

    # Handle form
    if request.method == 'POST':
        form = CutiForm(request.POST, request.FILES)
        if form.is_valid():
            cuti = form.save(commit=False)
            cuti.id_karyawan = karyawan
            cuti.save()

            # 🔔 Kirim notifikasi ke HRD
            hr_users = User.objects.filter(role='HRD')
            notify.send(
                sender=request.user,
                recipient=hr_users,
                verb="mengajukan cuti",
                description=f"{karyawan.nama} mengajukan cuti dari {cuti.tanggal_mulai} sampai {cuti.tanggal_selesai}",
                target=cuti,
                data={"url": "/hrd/approval-cuti/"}
            )

            messages.success(request, "Pengajuan cuti berhasil dikirim.")
            return redirect('pengajuan_cuti')
    else:
        form = CutiForm()

    # Data riwayat
    riwayat = Cuti.objects.filter(id_karyawan=karyawan).order_by('-created_at')

    #  Ambil tahun sekarang
    tahun_sekarang = timezone.now().year

    #  Ambil jatah cuti tahunan (asumsi hanya 1 objek per tahun per karyawan)
    jatah = JatahCuti.objects.filter(karyawan=karyawan, tahun=tahun_sekarang).first()
    
    # paginasi
    paginator = Paginator(riwayat, 10)  # Show 10 rules per page
    page_number = request.GET.get('page')
    riwayat = paginator.get_page(page_number)  # Get the current page's rules

    if jatah:
        total_jatah_cuti = jatah.total_cuti
        sisa_cuti = jatah.sisa_cuti
        cuti_terpakai = total_jatah_cuti - sisa_cuti
        persentase_penggunaan = round((cuti_terpakai / total_jatah_cuti) * 100) if total_jatah_cuti else 0
    else:
        total_jatah_cuti = 0
        sisa_cuti = 0
        cuti_terpakai = 0
        persentase_penggunaan = 0

    return render(request, 'karyawan/pengajuan_cuti.html', {
        'form': form,
        'riwayat': riwayat,
        'tahun_sekarang': tahun_sekarang,
        'total_jatah_cuti': total_jatah_cuti,
        'sisa_cuti': sisa_cuti,
        'cuti_terpakai': cuti_terpakai,
        'persentase_penggunaan': persentase_penggunaan,
    })


@login_required
def hapus_cuti_view(request, id):
    karyawan = get_object_or_404(Karyawan, user=request.user)

    #  Batasi hanya role yang diizinkan menghapus
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
