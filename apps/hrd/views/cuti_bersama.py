from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.hrd.models import CutiBersama, Karyawan, TidakAmbilCuti
from apps.hrd.forms import CutiBersamaForm
from apps.hrd.utils.jatah_cuti import hitung_jatah_cuti, isi_cuti_bersama

@login_required
def input_cuti_bersama_view(request):
    if request.GET.get("hapus_id"):
        try:
            cuti_dihapus = CutiBersama.objects.get(id=request.GET.get("hapus_id"))
            tahun = cuti_dihapus.tanggal.year
            
            # Simpan referensi sebelum menghapus
            tanggal_dihapus = cuti_dihapus.tanggal
            keterangan_dihapus = cuti_dihapus.keterangan
            
            # Hapus cuti bersama
            cuti_dihapus.delete()

            # Proses karyawan yang tidak mengajukan tidak ambil cuti
            semua_karyawan = Karyawan.objects.all()
            for karyawan in semua_karyawan:
                if karyawan.user.role in ['HRD', 'Karyawan Tetap']:
                    sudah_ajukan = TidakAmbilCuti.objects.filter(
                        id_karyawan=karyawan,
                        status='disetujui',
                        tanggal__tanggal=tanggal_dihapus
                    ).exists()

                    if not sudah_ajukan:
                        # Cari detail jatah cuti yang terkait dengan cuti bersama ini
                        detail_list = DetailJatahCuti.objects.filter(
                            jatah_cuti__karyawan=karyawan,
                            jatah_cuti__tahun=tahun,
                            dipakai=True,
                            keterangan__contains=f'Cuti Bersama: {keterangan_dihapus or tanggal_dihapus}'
                        )
                        
                        # Jika ditemukan, tandai sebagai tidak dipakai
                        if detail_list.exists():
                            for detail in detail_list:
                                detail.dipakai = False
                                detail.jumlah_hari = 0
                                detail.keterangan = f'Dikembalikan: {keterangan_dihapus or tanggal_dihapus} (dihapus)'
                                detail.save()
                                
                                # Tambah sisa cuti
                                jatah_cuti = detail.jatah_cuti
                                jatah_cuti.sisa_cuti += 1
                                jatah_cuti.save()
                        else:
                            # Jika tidak ditemukan detail spesifik, gunakan hitung_jatah_cuti
                            hitung_jatah_cuti(karyawan, tahun)

            messages.success(request, f"Cuti bersama {tanggal_dihapus} berhasil dihapus dan jatah cuti dikembalikan.")
            return redirect('input_cuti_bersama')
        except CutiBersama.DoesNotExist:
            messages.error(request, "Data tidak ditemukan.")

    # Tambah cuti bersama
    if request.method == 'POST':
        form = CutiBersamaForm(request.POST)
        if form.is_valid():
            cuti_bersama = form.save()
            
            # Isi jatah cuti untuk semua karyawan
            tahun = cuti_bersama.tanggal.year
            isi_cuti_bersama(tahun)
            
            messages.success(request, f"Cuti bersama tanggal {cuti_bersama.tanggal} berhasil ditambahkan.")
            return redirect('input_cuti_bersama')
    else:
        form = CutiBersamaForm()

    daftar_cuti_bersama = CutiBersama.objects.all().order_by('-tanggal')
    return render(request, 'hrd/input_cuti_bersama.html', {
        'form': form,
        'daftar_cuti_bersama': daftar_cuti_bersama
    })
