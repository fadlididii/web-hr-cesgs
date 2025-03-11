from django.contrib import admin
from django.urls import include, path
from apps.authentication import views as auth_views  # Import langsung view login

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", auth_views.login_view, name="home"),  # Langsung load halaman login di root
    path("auth/", include("apps.authentication.urls")),
    path("hrd/", include("apps.hrd.urls")),
    path('karyawan/', include('apps.karyawan.urls_karyawan')),
    path('magang/', include('apps.karyawan.urls_magang')),
    path('profil/', include('apps.profil.urls')),
]
