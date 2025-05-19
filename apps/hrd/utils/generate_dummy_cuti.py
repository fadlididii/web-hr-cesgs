from django.utils import timezone
from datetime import datetime, date, timedelta
import random
from apps.hrd.models import Karyawan, JatahCuti, DetailJatahCuti, CutiBersama
from apps.hrd.utils.jatah_cuti import hitung_jatah_cuti, isi_cuti_tahunan
from django.db import transaction

def generate_dummy_cuti():
    """
    Fungsi untuk membuat data dummy jatah cuti dari karyawan yang sudah ada
    """
    # Ambil semua karyawan yang sudah ada di database
    karyawan_list = Karyawan.objects.all()
    
    if not karyawan_list.exists():
        print("Tidak ada karyawan di database. Silakan tambahkan karyawan terlebih dahulu.")
        return
    
    # Buat cuti bersama untuk 2023 dan 2024 jika belum ada
    cuti_bersama_2023 = [
        {'tanggal': date(2023, 1, 1), 'keterangan': 'Tahun Baru 2023'},
        {'tanggal': date(2023, 4, 22), 'keterangan': 'Idul Fitri 2023'},
        {'tanggal': date(2023, 4, 23), 'keterangan': 'Idul Fitri 2023'},
        {'tanggal': date(2023, 12, 25), 'keterangan': 'Natal 2023'},
    ]
    
    cuti_bersama_2024 = [
        {'tanggal': date(2024, 1, 1), 'keterangan': 'Tahun Baru 2024'},
        {'tanggal': date(2024, 4, 10), 'keterangan': 'Idul Fitri 2024'},
        {'tanggal': date(2024, 4, 11), 'keterangan': 'Idul Fitri 2024'},
        {'tanggal': date(2024, 12, 25), 'keterangan': 'Natal 2024'},
    ]
    
    with transaction.atomic():
        # Buat cuti bersama jika belum ada
        for data in cuti_bersama_2023 + cuti_bersama_2024:
            CutiBersama.objects.get_or_create(
                tanggal=data['tanggal'],
                defaults={'keterangan': data['keterangan']}
            )
        
        # Generate jatah cuti untuk setiap karyawan
        for karyawan in karyawan_list:
            print(f"Memproses karyawan: {karyawan.nama}")
            
            # Generate untuk 2023
            jatah_2023 = hitung_jatah_cuti(karyawan, 2023)
            
            # Simulasi pengambilan cuti di 2023 (jika karyawan sudah bekerja di 2023)
            if karyawan.mulai_kontrak and karyawan.mulai_kontrak.year <= 2023:
                # Ambil cuti random di pertengahan tahun
                bulan_cuti = random.randint(max(karyawan.mulai_kontrak.month, 1), 12)
                hari_cuti = random.randint(1, 20)
                
                # Pastikan tanggal valid
                try:
                    tanggal_mulai = date(2023, bulan_cuti, hari_cuti)
                    tanggal_selesai = tanggal_mulai + timedelta(days=random.randint(1, 3))
                    
                    # Pastikan tanggal selesai tidak melebihi akhir bulan
                    if tanggal_selesai.month != bulan_cuti:
                        tanggal_selesai = date(2023, bulan_cuti, 28)
                    
                    print(f"  - Mengambil cuti: {tanggal_mulai} s/d {tanggal_selesai}")
                    isi_cuti_tahunan(karyawan, tanggal_mulai, tanggal_selesai)
                except ValueError:
                    # Jika tanggal tidak valid, coba tanggal lain
                    try:
                        tanggal_mulai = date(2023, bulan_cuti, 1)
                        tanggal_selesai = date(2023, bulan_cuti, 3)
                        print(f"  - Mengambil cuti: {tanggal_mulai} s/d {tanggal_selesai}")
                        isi_cuti_tahunan(karyawan, tanggal_mulai, tanggal_selesai)
                    except Exception as e:
                        print(f"  - Gagal mengisi cuti: {str(e)}")
            
            # Generate untuk 2024
            jatah_2024 = hitung_jatah_cuti(karyawan, 2024)
            
            # Simulasi pengambilan cuti di 2024 (hanya untuk beberapa karyawan)
            if karyawan.mulai_kontrak and karyawan.mulai_kontrak.year <= 2024 and random.choice([True, False]):
                try:
                    bulan_cuti = random.randint(1, 3)  # Hanya ambil cuti di awal tahun
                    tanggal_mulai = date(2024, bulan_cuti, 15)
                    tanggal_selesai = tanggal_mulai + timedelta(days=random.randint(1, 2))
                    print(f"  - Mengambil cuti 2024: {tanggal_mulai} s/d {tanggal_selesai}")
                    isi_cuti_tahunan(karyawan, tanggal_mulai, tanggal_selesai)
                except Exception as e:
                    print(f"  - Gagal mengisi cuti 2024: {str(e)}")
        
        print("\nData dummy jatah cuti berhasil dibuat!")

def tampilkan_ringkasan_cuti():
    """
    Fungsi untuk menampilkan ringkasan jatah cuti yang telah dibuat
    """
    print("\n=== RINGKASAN JATAH CUTI ===")
    
    for tahun in [2023, 2024]:
        print(f"\nTahun {tahun}:")
        jatah_list = JatahCuti.objects.filter(tahun=tahun).select_related('karyawan')
        
        if not jatah_list.exists():
            print(f"  Tidak ada data jatah cuti untuk tahun {tahun}")
            continue
        
        for jatah in jatah_list:
            print(f"  - {jatah.karyawan.nama}: Total={jatah.total_cuti}, Sisa={jatah.sisa_cuti}")
            
            # Tampilkan detail cuti yang diambil
            detail_dipakai = DetailJatahCuti.objects.filter(
                jatah_cuti=jatah,
                dipakai=True,
                keterangan__icontains='Cuti Tahunan'
            )
            
            if detail_dipakai.exists():
                print(f"    Cuti yang diambil:")
                for detail in detail_dipakai:
                    print(f"    * {detail.keterangan}")
            
            # Tampilkan carry forward
            detail_carry = DetailJatahCuti.objects.filter(
                jatah_cuti=jatah,
                keterangan__icontains='Carry Forward'
            )
            
            if detail_carry.exists():
                print(f"    Carry Forward:")
                for detail in detail_carry:
                    print(f"    * {detail.keterangan}")

# Cara menjalankan:
if __name__ == "__main__":
    generate_dummy_cuti()
    tampilkan_ringkasan_cuti()