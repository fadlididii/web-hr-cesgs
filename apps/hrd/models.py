from django.db import models
from django.utils.timezone import now
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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="karyawan")
    nama = models.CharField(max_length=100)
    nama_catatan_kehadiran = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Nama yang digunakan dalam catatan kehadiran"
    )
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

    def cek_status_kontrak(self):
        """Cek apakah batas kontrak sudah lewat, jika iya ubah status_keaktifan menjadi 'Tidak Aktif'."""
        if self.batas_kontrak and self.batas_kontrak < now().date():
            self.status_keaktifan = 'Tidak Aktif'
            self.save()

    def __str__(self):
        return self.nama

class Cuti(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
    ]

    JENIS_CUTI_CHOICES = [
        ('tahunan', 'Cuti Tahunan'),
        ('melahirkan', 'Cuti Melahirkan'),
        ('menikah', 'Cuti Menikah'),
        ('menikahkan', 'Cuti Menikahkan Anak'),
        ('berkabung', 'Cuti Berkabung'),
        ('khitan', 'Cuti Khitan Anak'),
        ('baptis', 'Cuti Baptis Anak'),
        ('istri_melahirkan', 'Cuti Istri Melahirkan/Keguguran'),
        ('sakit', 'Cuti Sakit'),
    ]

    id_karyawan = models.ForeignKey('hrd.Karyawan', on_delete=models.CASCADE)
    approval = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_cuti')
    absensi = models.ForeignKey('absensi.Absensi', on_delete=models.SET_NULL, null=True, blank=True)
    tanggal_pengajuan = models.DateField(auto_now_add=True)
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    jenis_cuti = models.CharField(max_length=50, choices=JENIS_CUTI_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    file_pengajuan = models.FileField(upload_to='cuti/file_pengajuan/', null=True, blank=True)
    file_dokumen_formal = models.FileField(
        upload_to='cuti/file_dokumen_formal/', null=True, blank=True,
        help_text='File .docx cuti yang ditandatangani'
    )
    file_persetujuan = models.FileField(upload_to='cuti/file_persetujuan/', null=True, blank=True)
    feedback_hr = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'cuti'

    def __str__(self):
        return f"{self.id_karyawan.nama} - {self.jenis_cuti} ({self.status})"

class Izin(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
    ]

    JENIS_IZIN_CHOICES = [
        ('telat', 'Izin Telat'),
        ('wfh', 'Izin WFH'),
    ]

    id_karyawan = models.ForeignKey('hrd.Karyawan', on_delete=models.CASCADE)
    approval = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_izin')
    absensi = models.ForeignKey('absensi.Absensi', on_delete=models.SET_NULL, null=True, blank=True)
    tanggal_pengajuan = models.DateField(auto_now_add=True)
    tanggal_izin = models.DateField()
    jenis_izin = models.CharField(max_length=50, choices=JENIS_IZIN_CHOICES)
    alasan = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    file_pengajuan = models.FileField(upload_to='izin/file_pengajuan/', null=True, blank=True)
    file_persetujuan = models.FileField(upload_to='izin/file_persetujuan/', null=True, blank=True)
    feedback_hr = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'izin'

    def __str__(self):
        return f"{self.id_karyawan.nama} - {self.jenis_izin} ({self.status})"


class JatahCuti(models.Model):
    karyawan = models.ForeignKey('Karyawan', on_delete=models.CASCADE)
    tahun = models.IntegerField()
    total_cuti = models.IntegerField(default=12)
    sisa_cuti = models.IntegerField(default=12)

    class Meta:
        unique_together = ('karyawan', 'tahun')
        db_table = 'jatah_cuti'

    def __str__(self):
        return f"{self.karyawan.nama} - {self.tahun} (Sisa: {self.sisa_cuti})"

class CutiBersama(models.Model):
    tanggal = models.DateField()
    keterangan = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'cuti_bersama'
        unique_together = ['tanggal']

    def __str__(self):
        return f"{self.tanggal} - {self.keterangan or 'Cuti Bersama'}"

class TidakAmbilCuti(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
    ]

    id_karyawan = models.ForeignKey(Karyawan, on_delete=models.CASCADE)
    tanggal = models.ManyToManyField('CutiBersama', blank=True)
    alasan = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    file_pengajuan = models.FileField(upload_to='tidak_ambil_cuti/file_pengajuan/', null=True, blank=True)
    file_persetujuan = models.FileField(upload_to='tidak_ambil_cuti/file_persetujuan/', null=True, blank=True)
    approval = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_tidak_ambil_cuti')
    tanggal_pengajuan = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'tidak_ambil_cuti'

    def __str__(self):
        return f"{self.id_karyawan.nama} - Tidak Ambil Cuti ({self.status})"