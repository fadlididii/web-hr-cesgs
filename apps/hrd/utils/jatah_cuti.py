from apps.hrd.models import JatahCuti, CutiBersama
from datetime import datetime

def hitung_jatah_cuti(karyawan, tahun=None):
    tahun = tahun or datetime.now().year
    jatah, created = JatahCuti.objects.get_or_create(karyawan=karyawan, tahun=tahun)

    if not created and jatah.total_cuti and jatah.sisa_cuti:
        return jatah  # Sudah pernah dihitung

    # Hitung cuti proporsional berdasarkan bulan masuk
    bulan_masuk = karyawan.mulai_kontrak.month if karyawan.mulai_kontrak and karyawan.mulai_kontrak.year == tahun else 1
    bulan_aktif = 12 - bulan_masuk + 1
    total_cuti = round((12 / 12) * bulan_aktif)

    # Kurangi berdasarkan jumlah cuti bersama di tahun tersebut
    jumlah_cuti_bersama = CutiBersama.objects.filter(tanggal__year=tahun).count()
    sisa = max(0, total_cuti - jumlah_cuti_bersama)

    jatah.total_cuti = total_cuti
    jatah.sisa_cuti = sisa
    jatah.save()

    return jatah
