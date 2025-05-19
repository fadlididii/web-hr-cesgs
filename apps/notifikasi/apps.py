from django.apps import AppConfig

class NotifikasiConfig(AppConfig):
    name = 'apps.notifikasi'
    label = 'notifikasi'  # Penting: gunakan label yang berbeda
    verbose_name = 'Notifikasi'
    
    def ready(self):
        import apps.notifikasi.signals