from django.urls import path, include

urlpatterns = [
    path('', include('apps.karyawan.urls_karyawan')),  # untuk karyawan biasa
    path('magang/', include('apps.karyawan.urls_magang')),  # untuk magang
]
