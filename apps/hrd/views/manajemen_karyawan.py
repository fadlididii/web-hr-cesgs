from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.contrib import messages
from ..models import Karyawan
from ..forms import KaryawanForm
from apps.hrd.utils.jatah_cuti import hitung_jatah_cuti
from apps.authentication.models import User
from django.core.paginator import Paginator
import pandas as pd
from django.http import HttpResponse
from django.db.models import Q

@login_required
def list_karyawan(request):
    # **🔹 Gunakan QuerySet untuk Query Langsung ke Database**
    filters = Q()
    
    # Ambil filter dari GET request
    selected_nama = request.GET.get('nama', '').strip()
    selected_nama_ck = request.GET.get('nama_catatan_kehadiran', '').strip()
    selected_role = request.GET.get('role', '').strip()
    status_keaktifan = request.GET.get('status_keaktifan', '').strip()
    selected_status = request.GET.get('status', '').strip()
    selected_divisi = request.GET.get('divisi', '').strip()
    selected_sort_by = request.GET.get('sort_by', 'nama').strip()

    # **🔹 Tambahkan Filter ke QuerySet**
    if selected_nama:
        filters &= Q(nama__icontains=selected_nama)
    if selected_nama_ck:
        filters &= Q(nama_catatan_kehadiran__icontains=selected_nama_ck)
    if selected_role:
        filters &= Q(user__role=selected_role)
    if status_keaktifan:
        filters &= Q(status_keaktifan=status_keaktifan)
    if selected_status:
        filters &= Q(status=selected_status)
    if selected_divisi:
        filters &= Q(divisi__icontains=selected_divisi)

    # **🔹 Ambil data langsung dari database dengan filter**
    karyawan_list = Karyawan.objects.select_related('user').filter(filters)

    # **🔹 Sorting Data Langsung di Database**
    sort_fields = {
        'nama': 'nama',
        'nama_catatan_kehadiran': 'nama_catatan_kehadiran',
        'jabatan': 'jabatan',
        'role': 'user__role',
        'status_keaktifan': 'status_keaktifan',
    }
    karyawan_list = karyawan_list.order_by(sort_fields.get(selected_sort_by, 'nama'))

    # **🔹 Pilihan kolom yang bisa ditampilkan**
    available_columns = [
        ('nama', 'Nama'),
        ('nama_catatan_kehadiran', 'Nama Sesuai Catatan Kehadiran'),
        ('email', 'Email'),
        ('jabatan', 'Jabatan'),
        ('divisi', 'Divisi'),
        ('status', 'Status Perkawinan'),
        ('status_keaktifan', 'Status Keaktifan'),
        ('role', 'Role'),
        ('alamat', 'Alamat'),
        ('mulai_kontrak', 'Mulai Kontrak'),
        ('batas_kontrak', 'Batas Kontrak'),
        ('no_telepon', 'No Telepon'),
    ]

    # **🔹 Tangkap aksi select_all/unselect_all dari query parameter**
    select_action = request.GET.get('select_action')

    if select_action == 'select_all':
        selected_columns = [col[0] for col in available_columns]
    elif select_action == 'unselect_all':
        selected_columns = []
    else:
        selected_columns = request.GET.getlist('columns')

    # **🔹 Default: Tampilkan semua kolom jika belum dipilih**
    if not selected_columns:
        selected_columns = [col[0] for col in available_columns]

    # **🔹 Simpan ke session supaya pilihan kolom bertahan saat pindah halaman**
    request.session['selected_columns'] = selected_columns

    # **🔹 Paginasi (10 karyawan per halaman)**
    paginator = Paginator(karyawan_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'karyawan': page_obj,
        'roles': User.ROLE_CHOICES,
        'status_list': Karyawan.STATUS_CHOICES,
        'status_keaktifan_list': [
            ('Aktif', 'Aktif'),
            ('Tidak Aktif', 'Tidak Aktif')
        ],
        'selected_nama': selected_nama,
        'selected_nama_ck': selected_nama_ck,
        'selected_role': selected_role,
        'status_keaktifan': status_keaktifan,
        'selected_status': selected_status,
        'selected_divisi': selected_divisi,
        'selected_sort_by': selected_sort_by,
        'available_columns': available_columns,
        'selected_columns': selected_columns,
    }
    return render(request, 'hrd/manajemen_karyawan/index.html', context)


@login_required
def tambah_karyawan(request):
    if request.method == 'GET':
        storage = get_messages(request)
        for _ in storage:
            pass

    if request.method == 'POST':
        form = KaryawanForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email sudah terdaftar.')
                return redirect('tambah_karyawan')

            user = User.objects.create_user(
                email=email,
                password='CESGS123',
                role=role
            )

            karyawan = form.save(commit=False)
            karyawan.user = user
            karyawan.save()

            hitung_jatah_cuti(karyawan)

            messages.success(request, 'Karyawan baru berhasil ditambahkan.')
            return redirect('list_karyawan')
    else:
        form = KaryawanForm()

    return render(request, 'hrd/manajemen_karyawan/form.html', {'form': form})


@login_required
def edit_karyawan(request, id):
    karyawan = get_object_or_404(Karyawan, pk=id)

    if request.method == 'POST':
        form = KaryawanForm(request.POST, instance=karyawan)
        if form.is_valid():
            # Update ke tabel User
            karyawan.user.email = form.cleaned_data['email']
            karyawan.user.role = form.cleaned_data['role']
            karyawan.user.save()

            # Update ke tabel Karyawan
            form.save()

            messages.success(request, "Data karyawan berhasil diperbarui.")
            return redirect('list_karyawan')
    else:
        initial_data = {
            'email': karyawan.user.email,
            'role': karyawan.user.role,
        }
        form = KaryawanForm(instance=karyawan, initial=initial_data)

    return render(request, 'hrd/manajemen_karyawan/form.html', {
        'form': form,
        'is_edit': True
    })

@login_required
def hapus_karyawan(request, id):
    karyawan = get_object_or_404(Karyawan, pk=id)

    user = karyawan.user
    karyawan.delete()
    user.delete()

    messages.success(request, f"Karyawan {karyawan.nama} berhasil dihapus.")
    return redirect('list_karyawan')

@login_required
def download_karyawan_excel(request):
    # Ambil data dari model Karyawan
    data = Karyawan.objects.all().values(
        'nama', 'jabatan', 'divisi', 'status', 'status_keaktifan',
        'mulai_kontrak', 'batas_kontrak', 'no_telepon'
    )

    # Konversi ke DataFrame Pandas
    df = pd.DataFrame.from_records(data)

    # Buat file Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="data_karyawan.xlsx"'
    
    # Simpan DataFrame ke dalam file Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Karyawan')

    return response