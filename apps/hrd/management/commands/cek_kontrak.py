from django.core.management.base import BaseCommand
from apps.hrd.models import Karyawan
from django.utils.timezone import now

class Command(BaseCommand):
    help = "Menonaktifkan karyawan yang kontraknya sudah habis"

    def handle(self, *args, **kwargs):
        karyawan_berakhir = Karyawan.objects.filter(
            batas_kontrak__lt=now().date(),
            status_keaktifan='Aktif'
        )
        count = karyawan_berakhir.update(status_keaktifan='Tidak Aktif')
        self.stdout.write(self.style.SUCCESS(f"{count} karyawan dinonaktifkan."))
