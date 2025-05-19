from apps.hrd.models import JatahCuti, DetailJatahCuti, CutiBersama
from datetime import datetime, date

def hitung_jatah_cuti(karyawan, tahun=None):
    tahun = tahun or datetime.now().year

    # 1. Tentukan bulan masuk
    if karyawan.mulai_kontrak:
        if karyawan.mulai_kontrak.year < tahun:
            bulan_masuk = 1
        elif karyawan.mulai_kontrak.year == tahun:
            bulan_masuk = karyawan.mulai_kontrak.month
        else:
            return  # Belum berlaku tahun ini
    else:
        bulan_masuk = 1

    bulan_aktif = 12 - bulan_masuk + 1
    jatah_tahun_ini = bulan_aktif  # Jatah dasar untuk tahun ini

    # Cek akumulasi dari tahun-tahun sebelumnya
    akumulasi_total = 0
    for prev_year in range(tahun - 1, tahun - 4, -1):
        jatah_prev = JatahCuti.objects.filter(karyawan=karyawan, tahun=prev_year).first()
        if jatah_prev and jatah_prev.sisa_cuti > 0:
            akumulasi_total += jatah_prev.sisa_cuti

    # Batasi akumulasi maksimum
    max_akumulasi = 24
    akumulasi_final = min(akumulasi_total, max_akumulasi)
    
    # Total cuti adalah jatah tahun ini + akumulasi dari tahun sebelumnya
    total_cuti = jatah_tahun_ini + akumulasi_final

    # 2. Buat atau update jatah cuti
    jatah, _ = JatahCuti.objects.get_or_create(
        karyawan=karyawan,
        tahun=tahun,
        defaults={'total_cuti': total_cuti, 'sisa_cuti': total_cuti}
    )
    jatah.total_cuti = total_cuti
    jatah.sisa_cuti = total_cuti
    jatah.save()

    # 3. Hapus semua detail sebelumnya
    DetailJatahCuti.objects.filter(jatah_cuti=jatah).delete()

    # 4. Tandai bulan sebelum mulai kerja sebagai 'belum aktif'
    for bulan in range(1, bulan_masuk):
        DetailJatahCuti.objects.create(
            jatah_cuti=jatah,
            bulan=bulan,
            tahun=tahun,
            dipakai=True,
            jumlah_hari=0,
            keterangan='Belum aktif (belum mulai kerja)'
        )

    # 5. Buat detail cuti kosong untuk bulan aktif
    for bulan in range(bulan_masuk, 13):
        DetailJatahCuti.objects.create(
            jatah_cuti=jatah,
            bulan=bulan,
            tahun=tahun,
            dipakai=False,
            jumlah_hari=0,
            keterangan=''
        )

    # 6. Tambah carry forward dari tahun-tahun sebelumnya (dengan akumulasi)
    # Catat informasi akumulasi untuk referensi
    if akumulasi_total > 0:
        DetailJatahCuti.objects.create(
            jatah_cuti=jatah,
            bulan=0,  # Bulan 0 sebagai penanda khusus untuk informasi akumulasi
            tahun=tahun,
            dipakai=False,
            jumlah_hari=akumulasi_final,
            keterangan=f'Total akumulasi dari tahun sebelumnya: {akumulasi_total} hari (dibatasi maks {max_akumulasi})'
        )
    
    # Tambahkan detail untuk setiap tahun yang berkontribusi
    for prev_year in range(tahun - 1, tahun - 4, -1):
        jatah_prev = JatahCuti.objects.filter(karyawan=karyawan, tahun=prev_year).first()
        if jatah_prev and jatah_prev.sisa_cuti > 0:
            DetailJatahCuti.objects.create(
                jatah_cuti=jatah,
                bulan=0,  # Bulan 0 sebagai penanda khusus untuk informasi akumulasi
                tahun=tahun,
                dipakai=False,
                jumlah_hari=jatah_prev.sisa_cuti,
                keterangan=f'Akumulasi dari tahun {prev_year}: {jatah_prev.sisa_cuti} hari'
            )
    
    # Tambahkan carry forward ke detail cuti
    carry_forward = akumulasi_final
    detail_aktif = DetailJatahCuti.objects.filter(
        jatah_cuti=jatah,
        dipakai=False,
        keterangan='',
        bulan__gt=0  # Hanya ambil bulan normal (bukan penanda informasi)
    ).order_by('bulan')  # ambil dari awal

    for detail in detail_aktif:
        if carry_forward <= 0:
            break
        detail.keterangan = f'Carry Forward dari tahun-tahun sebelumnya (total akumulasi: {akumulasi_total})'
        detail.jumlah_hari = 1
        detail.save()
        carry_forward -= 1

    # 7. Tambahkan cuti bersama
    cb_list = list(CutiBersama.objects.filter(tanggal__year=tahun).order_by('tanggal'))
    max_cb = len(cb_list)

    detail_kosong = DetailJatahCuti.objects.filter(
        jatah_cuti=jatah,
        tahun=tahun,
        dipakai=False,
        keterangan=''
    ).order_by('bulan')[:max_cb]

    for detail, cb in zip(detail_kosong, cb_list):
        detail.dipakai = True
        detail.keterangan = cb.keterangan or 'Cuti Bersama'
        detail.jumlah_hari = 1
        detail.save()

    # 8. Tandai carry forward yang hangus (lebih dari 1 tahun)
    today = date.today()
    detail_carry = DetailJatahCuti.objects.filter(
        jatah_cuti=jatah,
        tahun=tahun,
        dipakai=False,
        keterangan__icontains='Carry Forward'
    )
    for detail in detail_carry:
        detail_date = date(detail.tahun, detail.bulan, 1)
        if (today - detail_date).days > 365:
            detail.keterangan = 'Hangus Carry Forward (expired)'
            detail.jumlah_hari = 0
            detail.save()

    # 9. Hitung ulang sisa cuti (hanya yang benar-benar kosong dan aktif)
    sisa = DetailJatahCuti.objects.filter(
        jatah_cuti=jatah,
        tahun=tahun,
        dipakai=False,
        keterangan__in=['', 'Carry Forward dari tahun sebelumnya', 'Carry Forward dari tahun-tahun sebelumnya (total akumulasi: {carry_forward_total})']
    ).count()
    jatah.sisa_cuti = sisa
    jatah.save()

    return jatah

def isi_cuti_tahunan(karyawan, tanggal_mulai, tanggal_selesai):
    # Hitung jumlah hari
    jumlah_hari = (tanggal_selesai - tanggal_mulai).days + 1
    tahun = tanggal_mulai.year
    
    # Cari atau buat objek CutiTahunan untuk tahun tersebut
    cuti_tahunan, created = CutiTahunan.objects.get_or_create(
        id_karyawan=karyawan,
        tahun=tahun,
        defaults={'sisa_cuti': 12}  # Default jatah cuti tahunan
    )
    
    # Kurangi sisa cuti tanpa validasi minimum 0
    cuti_tahunan.sisa_cuti -= jumlah_hari
    cuti_tahunan.save()
    
    # Catat penggunaan cuti
    for i in range(jumlah_hari):
        tanggal = tanggal_mulai + timedelta(days=i)
        PenggunaanCutiTahunan.objects.create(
            id_cuti_tahunan=cuti_tahunan,
            tanggal=tanggal
        )

    jatah = JatahCuti.objects.filter(karyawan=karyawan, tahun=tahun).first()
    if not jatah:
        return

    sisa_diisi = jumlah_hari

    detail_kosong = DetailJatahCuti.objects.filter(
        jatah_cuti=jatah,
        tahun=tahun,
        dipakai=False,
    ).order_by('bulan')

    for detail in detail_kosong:
        if sisa_diisi <= 0:
            break
        detail.dipakai = True
        detail.jumlah_hari = 1
        detail.keterangan = f'Cuti Tahunan {tanggal_mulai} s/d {tanggal_selesai}'
        detail.save()
        sisa_diisi -= 1

    jatah.sisa_cuti = max(0, jatah.sisa_cuti - jumlah_hari)
    jatah.save()

def kembalikan_jatah_tidak_ambil_cuti(karyawan, daftar_tanggal):
    tahun_list = set(tanggal.tanggal.year for tanggal in daftar_tanggal)

    for tahun in tahun_list:
        jatah = JatahCuti.objects.filter(karyawan=karyawan, tahun=tahun).first()
        if not jatah:
            continue

        detail_queryset = DetailJatahCuti.objects.filter(
            jatah_cuti=jatah,
            tahun=tahun,
            dipakai=True
        ).order_by('-bulan') 

        jumlah_kembali = sum(1 for tanggal in daftar_tanggal if tanggal.tanggal.year == tahun)

        for detail in detail_queryset:
            if jumlah_kembali <= 0:
                break
            detail.dipakai = False
            detail.jumlah_hari = 0
            detail.keterangan = ''
            detail.save()
            jumlah_kembali -= 1

        jatah.sisa_cuti = DetailJatahCuti.objects.filter(jatah_cuti=jatah, dipakai=False).count()
        jatah.save()

def rapikan_cuti_tahunan(karyawan, tahun):
    jatah = JatahCuti.objects.filter(karyawan=karyawan, tahun=tahun).first()
    if not jatah:
        return

    cuti_details = DetailJatahCuti.objects.filter(
        jatah_cuti=jatah,
        tahun=tahun,
        dipakai=True,
        keterangan__icontains='Cuti Tahunan'
    ).order_by('bulan')

    jumlah_cuti = cuti_details.count()
    cuti_details.update(dipakai=False, jumlah_hari=0, keterangan='')

    kosong_details = DetailJatahCuti.objects.filter(
        jatah_cuti=jatah,
        tahun=tahun,
        dipakai=False
    ).order_by('bulan')

    for detail in kosong_details:
        if jumlah_cuti <= 0:
            break
        detail.dipakai = True
        detail.jumlah_hari = 1
        detail.keterangan = 'Dirapikan otomatis setelah pengembalian cuti'
        detail.save()
        jumlah_cuti -= 1

def tandai_cuti_hangus(karyawan, tahun):
    today = date.today()
    jatah = JatahCuti.objects.filter(karyawan=karyawan, tahun=tahun).first()
    if not jatah:
        return

    details = DetailJatahCuti.objects.filter(
        jatah_cuti=jatah,
        tahun=tahun,
        dipakai=False
    )

    for detail in details:
        detail_date = date(detail.tahun, detail.bulan, 1)
        if (today - detail_date).days > 365:
            detail.keterangan = 'Hangus (lebih dari 1 tahun)'
            detail.jumlah_hari = 0
            detail.save()
