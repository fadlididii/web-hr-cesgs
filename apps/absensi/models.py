from django.db import models
from apps.hrd.models import Karyawan

class Rules(models.Model):
    id_rules = models.AutoField(primary_key=True)
    nama_rule = models.CharField(max_length=100, unique=True)  # Contoh: "Jam Kerja Standar"
    jam_masuk = models.TimeField()
    jam_keluar = models.TimeField()
    toleransi_telat = models.IntegerField(default=15, help_text="Toleransi keterlambatan dalam menit")
    maksimal_izin = models.IntegerField(default=3, help_text="Jumlah maksimal izin dalam sebulan")
    
    created_at = models.DateTimeField(auto_now_add=True)  # Waktu dibuat
    updated_at = models.DateTimeField(auto_now=True)  # Waktu terakhir diperbarui

    def __str__(self):
        return self.nama_rule


class Absensi(models.Model):
    id_absensi = models.AutoField(primary_key=True)
    id_karyawan = models.ForeignKey(Karyawan, on_delete=models.CASCADE)
    rules = models.ForeignKey(Rules, on_delete=models.SET_NULL, null=True, blank=True)
    tanggal = models.DateField()
    bulan = models.IntegerField()
    tahun = models.IntegerField()
    
    status_absensi = models.CharField(
        max_length=20, 
        choices=[
            ('Hadir', 'Hadir'),
            ('Terlambat', 'Terlambat'),
            ('Izin', 'Izin'),
            ('Sakit', 'Sakit'),
            ('Libur', 'Libur')
        ]
    )
    jam_masuk = models.TimeField(null=True, blank=True)
    jam_keluar = models.TimeField(null=True, blank=True)
    is_libur = models.BooleanField(default=False)

    # ✅ Kolom tambahan untuk menyimpan informasi file upload
    nama_file = models.CharField(max_length=255, null=True, blank=True)  # Nama file yang diunggah
    file_url = models.CharField(max_length=500, null=True, blank=True)  # URL file di media storage
    created_at = models.DateTimeField(auto_now_add=True)  # Waktu upload pertama kali

    def __str__(self):
        return f"Absensi {self.id_karyawan.nama} - {self.tanggal} ({self.status_absensi})"