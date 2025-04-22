from django.urls import path
from .views.dashboard import hrd_dashboard
from apps.hrd.views.hrd_cuti import approval_cuti_view, export_riwayat_cuti_excel
from apps.hrd.views.hrd_izin import approval_izin_view, export_riwayat_izin_excel
from .views.cuti_bersama import input_cuti_bersama_view
from .views.manajemen_karyawan import list_karyawan, tambah_karyawan, edit_karyawan, hapus_karyawan, download_karyawan_excel
from apps.hrd.views.jatah_cuti import lihat_jatah_cuti_view

urlpatterns = [
    path('', hrd_dashboard, name='hrd_dashboard'),
    path('approval-cuti/', approval_cuti_view, name='approval_cuti'),
    path('approval-izin/', approval_izin_view, name='approval_izin'),
    path('manajemen-karyawan/', list_karyawan, name='list_karyawan'),
    path('manajemen-karyawan/tambah/', tambah_karyawan, name='tambah_karyawan'),
    path('manajemen-karyawan/edit/<int:id>/', edit_karyawan, name='edit_karyawan'),
    path('manajemen-karyawan/hapus/<int:id>/', hapus_karyawan, name='hapus_karyawan'),
    path('download-karyawan/', download_karyawan_excel, name='download_karyawan'),
    path('cuti-bersama/', input_cuti_bersama_view, name='input_cuti_bersama'),
    path('jatah-cuti/', lihat_jatah_cuti_view, name='lihat_jatah_cuti'),
    path('approval-cuti/export/', export_riwayat_cuti_excel, name='export_riwayat_cuti_excel'),
    path('approval-izin/export/', export_riwayat_izin_excel, name='export_riwayat_izin_excel'),
]
