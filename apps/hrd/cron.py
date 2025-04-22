from django_cron import CronJobBase, Schedule
from apps.hrd.models import Karyawan
from django.utils.timezone import now

class CekKontrakKaryawan(CronJobBase):
    RUN_EVERY_MINS = 1440  # Jalankan setiap 24 jam (1440 menit)

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'hrd.cek_kontrak_karyawan'  # Kode unik untuk cron job ini

    def do(self):
        karyawan_berakhir = Karyawan.objects.filter(
            batas_kontrak__lt=now().date(),
            status_keaktifan='Aktif'
        )
        count = karyawan_berakhir.update(status_keaktifan='Tidak Aktif')
        print(f"{count} karyawan dinonaktifkan.")  # Debugging
