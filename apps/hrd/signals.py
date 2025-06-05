from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import JatahCuti, DetailJatahCuti, Karyawan, CutiBersama
from datetime import datetime
from apps.hrd.utils.jatah_cuti import hitung_jatah_cuti

@receiver(post_save, sender=JatahCuti)
def create_detail_jatah_cuti(sender, instance, created, **kwargs):
    if created:
        for bulan in range(1, 13):
            DetailJatahCuti.objects.create(
                jatah_cuti=instance,
                bulan=bulan,
                tahun=instance.tahun,
                dipakai=False,
                jumlah_hari=0,
                keterangan=''
            )

@receiver(post_save, sender=Karyawan)
def create_jatah_cuti(sender, instance, created, **kwargs):
    if created and hasattr(instance, 'user') and instance.user.role in ['HRD', 'Karyawan Tetap']:
        tahun_ini = datetime.now().year
        hitung_jatah_cuti(instance, tahun=tahun_ini)

# Hapus atau modifikasi handler ini karena kita sudah menangani pengembalian jatah cuti
# di input_cuti_bersama_view
@receiver(post_delete, sender=CutiBersama)
def reset_jatah_setelah_cb_dihapus(sender, instance, **kwargs):
    # Tidak perlu melakukan apa-apa karena sudah ditangani di view
    pass
    tahun = instance.tanggal.year
    for karyawan in Karyawan.objects.all():
        if hasattr(karyawan, 'user') and karyawan.user.role in ['HRD', 'Karyawan Tetap']:
            hitung_jatah_cuti(karyawan, tahun=tahun)
