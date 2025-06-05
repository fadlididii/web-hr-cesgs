from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from ..models import Karyawan
from ..forms import KaryawanForm
from apps.authentication.models import User
from apps.hrd.utils.jatah_cuti import hitung_jatah_cuti
from apps.hrd.utils.generate_password import generate_default_password
import pandas as pd

@login_required
def list_karyawan(request):
    filters = Q()
    selected_nama = request.GET.get('nama', '').strip()
    selected_role = request.GET.get('role', '').strip()
    status_keaktifan = request.GET.get('status_keaktifan', '').strip()
    selected_jenis_kelamin = request.GET.get('jenis_kelamin', '').strip()
    selected_divisi = request.GET.get('divisi', '').strip()
    selected_sort_by = request.GET.get('sort_by', 'nama').strip()
    select_action = request.GET.get('select_action')

    if selected_nama:
        filters &= Q(nama__icontains=selected_nama)
    if selected_role:
        filters &= Q(user__role=selected_role)
    if status_keaktifan:
        filters &= Q(status_keaktifan=status_keaktifan)
    if selected_jenis_kelamin:
        filters &= Q(jenis_kelamin=selected_jenis_kelamin)
    if selected_divisi:
        filters &= Q(divisi=selected_divisi)

    karyawan_list = Karyawan.objects.select_related('user').filter(filters)

    sort_fields = {
        'nama': 'nama',
        'jabatan': 'jabatan',
        'role': 'user__role',
        'status_keaktifan': 'status_keaktifan',
    }
    karyawan_list = karyawan_list.order_by(sort_fields.get(selected_sort_by, 'nama'))

    available_columns = [
        ('nama', 'Nama'),
        ('nama_catatan_kehadiran', 'Nama Sesuai Catatan Kehadiran'),
        ('email', 'Email'),
        ('jenis_kelamin', 'Jenis Kelamin'),
        ('jabatan', 'Jabatan'),
        ('divisi', 'Divisi'),
        ('tanggal_lahir', 'Tanggal Lahir'),
        ('status', 'Status Perkawinan'),
        ('status_keaktifan', 'Status Keaktifan'),
        ('role', 'Role'),
        ('alamat', 'Alamat'),
        ('mulai_kontrak', 'Mulai Kontrak'),
        ('batas_kontrak', 'Batas Kontrak'),
        ('no_telepon', 'No Telepon'),
    ]

    if select_action == 'select_all':
        selected_columns = [col[0] for col in available_columns]
    elif select_action == 'unselect_all':
        selected_columns = []
    else:
        selected_columns = request.GET.getlist('columns') or request.session.get('selected_columns', [])

    if not selected_columns:
        selected_columns = [col[0] for col in available_columns]

    request.session['selected_columns'] = selected_columns

    paginator = Paginator(karyawan_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Update context
    context = {
        'karyawan': page_obj,
        'roles': User.ROLE_CHOICES,
        'status_keaktifan_list': [('Aktif', 'Aktif'), ('Tidak Aktif', 'Tidak Aktif')],
        'divisi_list': Karyawan.DIVISI_CHOICES,
        'selected_nama': selected_nama,
        'selected_role': selected_role,
        'status_keaktifan': status_keaktifan,
        'selected_divisi': selected_divisi,
        'selected_sort_by': selected_sort_by,
        'available_columns': available_columns,
        'selected_columns': selected_columns,
        'jenis_kelamin_list': Karyawan.JENIS_KELAMIN_CHOICES,
        'selected_jenis_kelamin': selected_jenis_kelamin,
    }

    # Jika permintaan berasal dari AJAX, kembalikan hanya tabelnya
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'hrd/manajemen_karyawan/tabel_karyawan.html', context)

    return render(request, 'hrd/manajemen_karyawan/index.html', context)

@login_required
def tambah_karyawan(request):
    if request.method == 'POST':
        form = KaryawanForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            nama = form.cleaned_data['nama']
            tgl_lahir = form.cleaned_data['tanggal_lahir']

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email sudah terdaftar.')
                return redirect('tambah_karyawan')

            # Simpan karyawan dulu tanpa user
            karyawan = form.save(commit=False)

            password_default = generate_default_password(nama, tgl_lahir)

            # Buat user
            user = User.objects.create_user(
                email=email,
                role=role,
                password=password_default
            )

            # Assign dan simpan ulang
            karyawan.user = user
            karyawan.save()

            messages.success(request, f'Data karyawan berhasil ditambahkan. Password: {password_default}')
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
            karyawan.user.email = form.cleaned_data['email']
            karyawan.user.role = form.cleaned_data['role']
            karyawan.user.save()
            form.save()
            messages.success(request, "Data karyawan berhasil diperbarui.")
            return redirect('list_karyawan')
    else:
        initial_data = {
            'email': karyawan.user.email,
            'role': karyawan.user.role,
        }
        form = KaryawanForm(instance=karyawan, initial=initial_data)

    return render(request, 'hrd/manajemen_karyawan/form.html', {'form': form, 'is_edit': True})


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
    data = Karyawan.objects.all().values(
        'nama', 'jenis_kelamin', 'jabatan', 'divisi', 'status', 'status_keaktifan',
        'mulai_kontrak', 'batas_kontrak', 'no_telepon'
    )
    df = pd.DataFrame.from_records(data)
    
    # Konversi kode jenis kelamin ke label yang lebih jelas
    jenis_kelamin_map = dict(Karyawan.JENIS_KELAMIN_CHOICES)
    df['jenis_kelamin'] = df['jenis_kelamin'].map(jenis_kelamin_map)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="data_karyawan.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Karyawan')
    return response
