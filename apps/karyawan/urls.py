from django.urls import path
from .views import karyawan_views, magang_views

urlpatterns = [
    path('', karyawan_views.karyawan_dashboard, name='karyawan_dashboard'),
    path('pengajuan-cuti/', karyawan_views.pengajuan_cuti, name='pengajuan_cuti'),
    path('pengajuan-izin/', karyawan_views.pengajuan_izin, name='pengajuan_izin'),
    path('edit-profil/', karyawan_views.edit_profil, name='edit_profil'),

    # Fitur Magang
    path('magang/', magang_views.magang_dashboard, name='magang_dashboard'),
    path('magang/edit-profil/', magang_views.edit_profil_magang, name='edit_profil_magang'),
]