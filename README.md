## Cara Menjalankan Aplikasi

1. Clone Repository
2. buat virtual env
3. pip install -r requirements.txt
4. sesuaikan .env
5. migrasi database
- python manage.py makemigrations
- python manage.py migrate
6. buat superakun (akun admin)
- buka cmd 
- run "python manage.py createsuperuser"
- isi email, role: (HRD, Karyawan Tetap, Magang), password
7. run server
- python manage.py runserver