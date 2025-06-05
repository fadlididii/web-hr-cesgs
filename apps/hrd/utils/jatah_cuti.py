from datetime import datetime, timedelta
from django.db.models import Q
from apps.hrd.models import JatahCuti, DetailJatahCuti, CutiBersama

def hitung_jatah_cuti(karyawan, tahun):
    """
    Menghitung jatah cuti karyawan untuk tahun tertentu.
    Fungsi ini akan membuat atau memperbarui record JatahCuti dan DetailJatahCuti.
    """
    # Cek apakah sudah ada jatah cuti untuk karyawan dan tahun ini
    jatah_cuti, created = JatahCuti.objects.get_or_create(
        karyawan=karyawan,
        tahun=tahun,
        defaults={
            'total_cuti': 12,  # Default 12 hari per tahun
            'sisa_cuti': 12
        }
    )
    
    # Jika tidak baru dibuat, reset detail jatah cuti
    if not created:
        # Reset semua detail jatah cuti yang belum dipakai
        DetailJatahCuti.objects.filter(
            jatah_cuti=jatah_cuti,
            dipakai=False
        ).update(jumlah_hari=0, keterangan='')
    
    # Ambil semua cuti bersama untuk tahun ini
    cuti_bersama = CutiBersama.objects.filter(tanggal__year=tahun)
    
    # Hitung total cuti bersama
    total_cuti_bersama = cuti_bersama.count()
    
    # Update total dan sisa cuti
    jatah_cuti.total_cuti = 12  # Reset ke default
    jatah_cuti.sisa_cuti = 12 - total_cuti_bersama  # Kurangi dengan cuti bersama
    jatah_cuti.save()
    

    return jatah_cuti

def isi_cuti_bersama(tahun):
    """Mengisi detail jatah cuti untuk cuti bersama."""
    # Ambil semua cuti bersama untuk tahun ini
    cuti_bersama = CutiBersama.objects.filter(tanggal__year=tahun).order_by('tanggal')
    total_cuti_bersama = cuti_bersama.count()
    
    if total_cuti_bersama == 0:
        return  # Tidak ada cuti bersama untuk diproses
    
    # Ambil semua karyawan tetap dan HRD yang aktif
    karyawan_list = Karyawan.objects.filter(
        Q(user__role='HRD') | Q(user__role='Karyawan Tetap'),
        status_keaktifan='Aktif'
    )
    
    for karyawan in karyawan_list:
        # Pastikan ada jatah cuti untuk tahun ini
        jatah_cuti = JatahCuti.objects.get_or_create(
            karyawan=karyawan,
            tahun=tahun,
            defaults={
                'total_cuti': 12,
                'sisa_cuti': 12 - total_cuti_bersama
            }
        )[0]
        
        # Buat daftar bulan yang akan diisi, mulai dari bulan terakhir tahun ini
        bulan_untuk_diisi = []
        tahun_saat_ini = tahun
        bulan_saat_ini = 12  # Mulai dari Desember tahun ini
        
        # Kumpulkan bulan-bulan yang akan diisi, sebanyak jumlah cuti bersama
        cuti_bersama_yang_perlu_diisi = []
        for cb in cuti_bersama:
            # Cek apakah karyawan sudah mengajukan untuk tidak ambil cuti bersama ini
            sudah_ajukan = karyawan.tidakambilcuti_set.filter(
                status='disetujui',
                tanggal=cb
            ).exists()
            
            if not sudah_ajukan:
                cuti_bersama_yang_perlu_diisi.append(cb)
        
        # Jika tidak ada cuti bersama yang perlu diisi untuk karyawan ini, lanjut ke karyawan berikutnya
        if not cuti_bersama_yang_perlu_diisi:
            continue
        
        # Cari bulan-bulan yang masih kosong, mulai dari Desember ke Januari
        jumlah_yang_perlu_diisi = len(cuti_bersama_yang_perlu_diisi)
        bulan_yang_diisi = 0
        
        while bulan_yang_diisi < jumlah_yang_perlu_diisi:
            # Cek apakah bulan ini masih kosong
            detail = DetailJatahCuti.objects.filter(
                jatah_cuti=jatah_cuti,
                tahun=tahun_saat_ini,
                bulan=bulan_saat_ini,
                dipakai=True
            ).first()
            
            if not detail:
                # Bulan ini masih kosong, tambahkan ke daftar yang akan diisi
                bulan_untuk_diisi.append((tahun_saat_ini, bulan_saat_ini))
                bulan_yang_diisi += 1
            
            # Pindah ke bulan sebelumnya
            bulan_saat_ini -= 1
            if bulan_saat_ini == 0:
                # Jika sudah sampai Januari, pindah ke Desember tahun sebelumnya
                tahun_saat_ini -= 1
                bulan_saat_ini = 12
        
        # Isi cuti bersama ke bulan-bulan yang sudah dikumpulkan
        for i, cb in enumerate(cuti_bersama_yang_perlu_diisi):
            if i < len(bulan_untuk_diisi):
                tahun_isi, bulan_isi = bulan_untuk_diisi[i]
                
                # Update atau buat detail jatah cuti
                detail, _ = DetailJatahCuti.objects.get_or_create(
                    jatah_cuti=jatah_cuti,
                    tahun=tahun_isi,
                    bulan=bulan_isi,
                    defaults={
                        'dipakai': True,
                        'jumlah_hari': 1,
                        'keterangan': f'Cuti Bersama: {cb.keterangan or cb.tanggal}'
                    }
                )
                
                # Jika detail sudah ada, update
                if not _:
                    detail.dipakai = True
                    detail.jumlah_hari = 1
                    detail.keterangan = f'Cuti Bersama: {cb.keterangan or cb.tanggal}'
                    detail.save()
                
                # Kurangi sisa cuti
                jatah_cuti.sisa_cuti = max(0, jatah_cuti.sisa_cuti - 1)
                jatah_cuti.save()

def isi_cuti_tahunan(karyawan, tanggal_mulai, tanggal_selesai):
    """Mengisi detail jatah cuti untuk cuti tahunan yang diajukan."""
    tahun = tanggal_mulai.year
    
    # Pastikan ada jatah cuti untuk tahun ini
    jatah_cuti = hitung_jatah_cuti(karyawan, tahun)
    
    # Hitung jumlah hari cuti
    jumlah_hari = 0
    current_date = tanggal_mulai
    while current_date <= tanggal_selesai:
        # Cek apakah tanggal ini adalah cuti bersama
        is_cuti_bersama = CutiBersama.objects.filter(tanggal=current_date).exists()
        
        # Jika bukan cuti bersama, hitung sebagai cuti tahunan
        if not is_cuti_bersama:
            jumlah_hari += 1
        
        current_date += timedelta(days=1)
    
    # Ambil semua bulan yang masih kosong, urutkan dari kiri ke kanan (Januari ke Desember)
    bulan_kosong = []
    for bulan in range(1, 13):
        detail = DetailJatahCuti.objects.filter(
            jatah_cuti=jatah_cuti,
            tahun=tahun,
            bulan=bulan,
            dipakai=True
        ).first()
        
        if not detail:
            bulan_kosong.append(bulan)
    
    # Jika tidak cukup bulan kosong, batalkan
    if len(bulan_kosong) < jumlah_hari:
        return False, "Jatah cuti tidak mencukupi"
    
    # Isi cuti tahunan dari bulan kosong pertama (dari kiri ke kanan)
    for i in range(jumlah_hari):
        if bulan_kosong:
            bulan = bulan_kosong.pop(0)  # Ambil bulan kosong pertama
            
            # Update atau buat detail jatah cuti
            detail, _ = DetailJatahCuti.objects.get_or_create(
                jatah_cuti=jatah_cuti,
                tahun=tahun,
                bulan=bulan,
                defaults={
                    'dipakai': True,
                    'jumlah_hari': 1,
                    'keterangan': f'Cuti Tahunan: {tanggal_mulai} - {tanggal_selesai}'
                }
            )
            
            # Jika detail sudah ada dan belum dipakai, update
            if not _:
                detail.dipakai = True
                detail.jumlah_hari = 1
                detail.keterangan = f'Cuti Tahunan: {tanggal_mulai} - {tanggal_selesai}'
                detail.save()
            
            # Kurangi sisa cuti
            jatah_cuti.sisa_cuti = max(0, jatah_cuti.sisa_cuti - 1)
            jatah_cuti.save()
    
    return True, "Berhasil mengisi jatah cuti"

def kembalikan_jatah_tidak_ambil_cuti(karyawan, daftar_tanggal):
    """Mengembalikan jatah cuti untuk karyawan yang tidak mengambil cuti bersama.
    Tambahan cuti akan mengosongkan bulan terakhir yang sebelumnya sudah terisi.
    
    Contoh: Jika sudah cuti dari Januari–Maret, dan mendapat tambahan 1 hari,
    maka bulan Maret akan dikosongkan kembali.
    """
    for tanggal in daftar_tanggal:
        tahun = tanggal.tanggal.year
        
        # Pastikan ada jatah cuti untuk tahun ini
        jatah_cuti = JatahCuti.objects.get_or_create(
            karyawan=karyawan,
            tahun=tahun,
            defaults={
                'total_cuti': 12,
                'sisa_cuti': 12
            }
        )[0]
        
        # Ambil semua detail jatah cuti yang dipakai, urutkan dari kanan ke kiri (Desember ke Januari)
        # Ini memastikan kita mengosongkan bulan terakhir yang terisi
        detail_terpakai = DetailJatahCuti.objects.filter(
            jatah_cuti=jatah_cuti,
            tahun=tahun,
            dipakai=True
        ).order_by('-bulan')
        
        if detail_terpakai.exists():
            # Ambil detail terakhir yang dipakai (bulan terbesar/terakhir)
            detail = detail_terpakai.first()
            
            # Kembalikan jatah cuti
            detail.dipakai = False
            detail.jumlah_hari = 0
            detail.keterangan = f'Tidak Ambil Cuti Bersama: {tanggal.tanggal}'
            detail.save()
            
            # Tambah sisa cuti
            jatah_cuti.sisa_cuti += 1
            jatah_cuti.save()

def cek_expired_cuti():
    """Cek jatah cuti yang sudah expired (lebih dari 1 tahun tidak digunakan)."""
    current_date = datetime.now().date()
    tahun_lalu = current_date.year - 1
    bulan_current = current_date.month
    
    # Ambil semua jatah cuti tahun lalu
    jatah_cuti_list = JatahCuti.objects.filter(tahun=tahun_lalu)
    
    expired_list = []
    
    for jatah_cuti in jatah_cuti_list:
        # Ambil detail jatah cuti yang belum dipakai dan bulannya <= bulan sekarang
        detail_list = DetailJatahCuti.objects.filter(
            jatah_cuti=jatah_cuti,
            tahun=tahun_lalu,
            bulan__lte=bulan_current,
            dipakai=False
        )
        
        for detail in detail_list:
            # Tandai sebagai expired
            detail.keterangan = f'Expired: {detail.keterangan}'
            detail.save()
            
            expired_list.append({
                'karyawan': jatah_cuti.karyawan.nama,
                'bulan': calendar.month_name[detail.bulan],
                'tahun': tahun_lalu
            })
    
    return expired_list


def rapikan_cuti_tahunan(karyawan, tahun):
    """Menyinkronkan total dan sisa cuti berdasarkan detail jatah cuti yang terpakai."""
    # Pastikan ada jatah cuti untuk tahun ini
    jatah_cuti = JatahCuti.objects.get_or_create(
        karyawan=karyawan,
        tahun=tahun,
        defaults={
            'total_cuti': 12,
            'sisa_cuti': 12
        }
    )[0]
    
    # Hitung jumlah detail jatah cuti yang dipakai
    jumlah_terpakai = DetailJatahCuti.objects.filter(
        jatah_cuti=jatah_cuti,
        tahun=tahun,
        dipakai=True
    ).count()
    
    # Update sisa cuti
    jatah_cuti.sisa_cuti = jatah_cuti.total_cuti - jumlah_terpakai
    jatah_cuti.save()
    
    return jatah_cuti