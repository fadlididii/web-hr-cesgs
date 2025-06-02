## Cara Menjalankan Aplikasi

1. Clone Repository
2. buat virtual env
3. pip install -r requirements.txt
4. sesuaikan .env
5. migrasi database
python manage.py makemigrations
python manage.py migrate
6. buat superakun (akun admin)
python manage.py createsuperuser
7. run server
python manage.py runserver
