from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from apps.authentication import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", auth_views.login_view, name="home"),
    path("auth/", include("apps.authentication.urls")),
    path("hrd/", include("apps.hrd.urls")),
    path("karyawan/", include("apps.karyawan.urls_karyawan")),
    path("magang/", include("apps.karyawan.urls_magang")),
    path("profil/", include("apps.profil.urls")),
    path("absensi/", include("apps.absensi.urls")),
    path('notifikasi/', include('apps.notifikasi.urls')), 
    path('inbox/notifications/', include('notifications.urls', namespace='notifications')), 
]

# Tambahkan konfigurasi untuk media files (agar file absensi bisa diakses)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
