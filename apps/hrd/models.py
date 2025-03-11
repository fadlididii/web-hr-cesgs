from django.db import models
from apps.authentication.models import User

class Karyawan(models.Model):
    STATUS_CHOICES = [
        ('Belum kawin', 'Belum kawin'),
        ('Kawin', 'Kawin'),
        ('Cerai hidup', 'Cerai hidup'),
        ('Cerai mati', 'Cerai mati'),
    ]

    STATUS_KEAKTIFAN_CHOICES = [
        ('Aktif', 'Aktif'),
        ('Tidak Aktif', 'Tidak Aktif')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # relasi ke User
    nama = models.CharField(max_length=100)
    jabatan = models.CharField(max_length=50)
    divisi = models.CharField(max_length=50)
    alamat = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    mulai_kontrak = models.DateField(null=True, blank=True)
    batas_kontrak = models.DateField(null=True, blank=True)
    status_keaktifan = models.CharField(max_length=15, choices=STATUS_KEAKTIFAN_CHOICES, default='Aktif')
    no_telepon = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        db_table = 'karyawan'

    def __str__(self):
        return self.nama
