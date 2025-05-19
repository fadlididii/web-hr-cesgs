from django.apps import AppConfig


class HrdConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hrd'
    
    def ready(self):
        import apps.hrd.signals