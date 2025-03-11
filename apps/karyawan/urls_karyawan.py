from django.urls import path
from .views import karyawan_views

urlpatterns = [
    path('', karyawan_views.karyawan_dashboard, name='karyawan_dashboard'),
    path('pengajuan-cuti/', karyawan_views.pengajuan_cuti, name='pengajuan_cuti'),
    path('pengajuan-izin/', karyawan_views.pengajuan_izin, name='pengajuan_izin'),
    path('edit-profil/', karyawan_views.edit_profil, name='edit_profil'),
]
