# Generated by Django 3.2.6 on 2025-03-18 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('absensi', '0002_auto_20250318_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='absensi',
            name='rules',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='absensi.rules'),
        ),
    ]
