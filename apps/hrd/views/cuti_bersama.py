from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.hrd.models import CutiBersama, JatahCuti, Karyawan, TidakAmbilCuti
from apps.hrd.forms import CutiBersamaForm
from apps.hrd.utils.jatah_cuti import hitung_jatah_cuti

@login_required
def input_cuti_bersama_view(request):
    # Handle hapus cuti bersama
    if request.GET.get("hapus_id"):
        try:
            cuti_dihapus = CutiBersama.objects.get(id=request.GET.get("hapus_id"))
            tahun = cuti_dihapus.tanggal.year

            semua_karyawan = Karyawan.objects.all()

            for karyawan in semua_karyawan:
                if karyawan.user.role in ['HRD', 'Karyawan Tetap']:
                    # ❗Cek apakah karyawan ini sudah mengajukan "tidak ambil cuti" dan disetujui untuk tanggal ini
                    sudah_ajukan = TidakAmbilCuti.objects.filter(
                        id_karyawan=karyawan,
                        status='disetujui',
                        tanggal=cuti_dihapus
                    ).exists()

                    if not sudah_ajukan:  # ➕ Tambahkan hanya jika belum pernah diajukan
                        jatah, _ = JatahCuti.objects.get_or_create(
                            karyawan=karyawan, tahun=tahun,
                            defaults={'total_cuti': 12, 'sisa_cuti': 12}
                        )
                        jatah.sisa_cuti += 1
                        jatah.save()

            cuti_dihapus.delete()
            messages.success(request, f"Cuti bersama {cuti_dihapus.tanggal} berhasil dihapus dan jatah cuti dikembalikan.")
            return redirect('input_cuti_bersama')
        except CutiBersama.DoesNotExist:
            messages.error(request, "Data tidak ditemukan.")

    # Tambah cuti bersama
    if request.method == 'POST':
        form = CutiBersamaForm(request.POST)
        if form.is_valid():
            tanggal = form.cleaned_data['tanggal']

            if CutiBersama.objects.filter(tanggal=tanggal).exists():
                messages.warning(request, f"Tanggal {tanggal} sudah ditambahkan sebelumnya.")
            else:
                cuti_bersama = form.save()
                tahun = cuti_bersama.tanggal.year

                # Kurangi jatah cuti semua karyawan
                semua_karyawan = Karyawan.objects.all()
                for karyawan in semua_karyawan:
                    if karyawan.user.role in ['HRD', 'Karyawan Tetap']:
                        jatah = hitung_jatah_cuti(karyawan, tahun)
                        jatah.sisa_cuti = max(0, jatah.sisa_cuti - 1)
                        jatah.save()

                messages.success(request, f"Cuti bersama {tanggal} berhasil ditambahkan dan jatah cuti dikurangi.")
                return redirect('input_cuti_bersama')
    else:
        form = CutiBersamaForm()

    daftar_cuti_bersama = CutiBersama.objects.all().order_by('-tanggal')
    return render(request, 'hrd/input_cuti_bersama.html', {
        'form': form,
        'daftar_cuti_bersama': daftar_cuti_bersama
    })
