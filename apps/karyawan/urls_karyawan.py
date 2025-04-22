from django.urls import path
from .views import karyawan_views
from .views.cuti import cuti_view, hapus_cuti_view
from .views.izin import izin_view, hapus_izin_view
from .views.tidak_ambil_cuti import tidak_ambil_cuti_view, hapus_tidak_ambil_cuti_view

urlpatterns = [
    path('', karyawan_views.karyawan_dashboard, name='karyawan_dashboard'),
    path('pengajuan-cuti/', cuti_view, name='pengajuan_cuti'),
    path('hapus-cuti/<int:id>/', hapus_cuti_view, name='hapus_cuti'),
    path('pengajuan-izin/', izin_view, name='pengajuan_izin'),
    path('hapus-izin/<int:id>/', hapus_izin_view, name='hapus_izin'),
    path('tidak-ambil-cuti/', tidak_ambil_cuti_view, name='tidak_ambil_cuti'),
    path('hapus-tidak-ambil-cuti/<int:id>/', hapus_tidak_ambil_cuti_view, name='hapus_tidak_ambil_cuti'),
    path('edit-profil/', karyawan_views.edit_profil, name='edit_profil'),
]
