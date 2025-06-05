from django_cron import CronJobBase, Schedule
from apps.hrd.models import Karyawan
from django.utils.timezone import now
from apps.hrd.utils.jatah_cuti import cek_expired_cuti

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

def cek_expired_cuti_job():
    """Cron job untuk mengecek jatah cuti yang sudah expired."""
    expired_list = cek_expired_cuti()
    
    # Kirim notifikasi ke HRD
    if expired_list:
        for user in User.objects.filter(role='HRD'):
            message = "Beberapa jatah cuti telah expired (lebih dari 1 tahun tidak digunakan):\n"
            for item in expired_list:
                message += f"- {item['karyawan']} - {item['bulan']} {item['tahun']}\n"
            
            notify.send(
                sender=user,
                recipient=user,
                verb="cuti_expired",
                description=message
            )
