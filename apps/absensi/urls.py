from django.urls import path
from apps.absensi.views.absensi_views import upload_absensi, delete_absensi, hapus_absensi_bulanan, export_absensi_excel
from apps.absensi.views.rules_views import list_rules, create_rule, update_rule, delete_rule
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ✅ 📂 Upload & Kelola Absensi
    path('upload/', upload_absensi, name='upload_absensi'),
    path('upload/delete/<int:id>/', delete_absensi, name='delete_absensi'),
    path('upload/hapus/', hapus_absensi_bulanan, name='hapus_absensi_bulanan'),
    path('absensi/export/', export_absensi_excel, name='export_absensi_excel'),

    # ✅ ⚖ Manajemen Rules Absensi
    path('rules/', list_rules, name='list_rules'),
    path('rules/tambah/', create_rule, name='create_rule'),
    path('rules/edit/<int:id>/', update_rule, name='update_rule'),
    path('rules/hapus/<int:id>/', delete_rule, name='delete_rule'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)