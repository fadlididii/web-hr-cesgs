from django.urls import path
from .views.dashboard import hrd_dashboard
# from .views.approval import approval_cuti, approval_izin
from .views.manajemen_karyawan import list_karyawan, tambah_karyawan, edit_karyawan, hapus_karyawan

urlpatterns = [
    path('', hrd_dashboard, name='hrd_dashboard'),
    # path('approval/cuti/', approval_cuti, name='approval_cuti'),
    # path('approval/izin/', approval_izin, name='approval_izin'),
    path('manajemen-karyawan/', list_karyawan, name='list_karyawan'),
    path('manajemen-karyawan/tambah/', tambah_karyawan, name='tambah_karyawan'),
    path('manajemen-karyawan/edit/<int:id>/', edit_karyawan, name='edit_karyawan'),
    path('manajemen-karyawan/hapus/<int:id>/', hapus_karyawan, name='hapus_karyawan'),
]
