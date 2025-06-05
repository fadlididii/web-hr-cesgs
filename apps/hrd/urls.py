from django.urls import path
from .views.dashboard import hrd_dashboard, calendar_events
from apps.hrd.views.hrd_cuti import approval_cuti_view, export_riwayat_cuti_excel
from apps.hrd.views.hrd_izin import approval_izin_view, export_riwayat_izin_excel
from .views.cuti_bersama import input_cuti_bersama_view
from .views.manajemen_karyawan import list_karyawan, tambah_karyawan, edit_karyawan, hapus_karyawan, download_karyawan_excel
from .views.laporan_jatah_cuti import laporan_jatah_cuti_view, export_laporan_jatah_cuti_excel, update_jatah_cuti_ajax, get_detail_jatah_cuti_ajax

urlpatterns = [
    path('', hrd_dashboard, name='hrd_dashboard'),
    path('kalender/events/', calendar_events, name='calendar_events'),
    path('approval-cuti/', approval_cuti_view, name='approval_cuti'),
    path('approval-izin/', approval_izin_view, name='approval_izin'),
    path('manajemen-karyawan/', list_karyawan, name='list_karyawan'),
    path('manajemen-karyawan/tambah/', tambah_karyawan, name='tambah_karyawan'),
    path('manajemen-karyawan/edit/<int:id>/', edit_karyawan, name='edit_karyawan'),
    path('manajemen-karyawan/hapus/<int:id>/', hapus_karyawan, name='hapus_karyawan'),
    path('download-karyawan/', download_karyawan_excel, name='download_karyawan'),
    path('cuti-bersama/', input_cuti_bersama_view, name='input_cuti_bersama'),
    path('approval-cuti/export/', export_riwayat_cuti_excel, name='export_riwayat_cuti_excel'),
    path('approval-izin/export/', export_riwayat_izin_excel, name='export_riwayat_izin_excel'),
    path('laporan-jatah-cuti/', laporan_jatah_cuti_view, name='laporan_jatah_cuti'),
    path('laporan-jatah-cuti/export/', export_laporan_jatah_cuti_excel, name='export_laporan_jatah_cuti_excel'),
    # Tambahkan endpoint AJAX baru
    path('laporan-jatah-cuti/update/', update_jatah_cuti_ajax, name='update_jatah_cuti_ajax'),
    path('laporan-jatah-cuti/detail/', get_detail_jatah_cuti_ajax, name='get_detail_jatah_cuti_ajax'),
]
