# Generated by Django 3.2.6 on 2025-04-29 17:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('hrd', '0014_tidakambilcuti_feedback_hr'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuti',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='izin',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='karyawan',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cuti',
            name='jenis_cuti',
            field=models.CharField(choices=[('tahunan', 'Cuti Tahunan'), ('melahirkan', 'Cuti Melahirkan (max: 90 hari)'), ('menikah', 'Cuti Menikah (max: 3 hari)'), ('menikahkan_anak', 'Cuti Menikahkan Anak (max: 2 hari)'), ('berkabung_sedarah', 'Cuti Berkabung: suami/istri, ortu, anak (max: 2 hari)'), ('berkabung_serumah', 'Cuti Berkabung: anggota serumah (max: 1 hari)'), ('khitan_anak', 'Cuti Khitan Anak (max: 2 hari)'), ('baptis_anak', 'Cuti Baptis Anak (max: 2 hari)'), ('istri_melahirkan', 'Cuti Istri Melahirkan/Keguguran (max: 2 hari)'), ('sakit', 'Cuti Sakit (lampirkan surat dokter)')], max_length=50),
        ),
    ]
