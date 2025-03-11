from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.contrib import messages
from ..models import Karyawan
from ..forms import KaryawanForm
from apps.authentication.models import User
from django.core.paginator import Paginator

@login_required
def list_karyawan(request):
    karyawan_list = Karyawan.objects.select_related('user')

    # Ambil filter dari GET request
    selected_nama = request.GET.get('nama', '').strip()
    selected_role = request.GET.get('role', '').strip()
    status_keaktifan = request.GET.get('status_keaktifan', '').strip()
    selected_status = request.GET.get('status', '').strip()
    selected_divisi = request.GET.get('divisi', '').strip()
    selected_sort_by = request.GET.get('sort_by', 'nama').strip()

    # Filter pencarian
    if selected_nama:
        karyawan_list = karyawan_list.filter(nama__icontains=selected_nama)
    if selected_role:
        karyawan_list = karyawan_list.filter(user__role=selected_role)
    if status_keaktifan:
        karyawan_list = karyawan_list.filter(status_keaktifan=status_keaktifan)
    if selected_status:
        karyawan_list = karyawan_list.filter(status=selected_status)
    if selected_divisi:
        karyawan_list = karyawan_list.filter(divisi__icontains=selected_divisi)

    # Sorting
    if selected_sort_by == 'nama':
        karyawan_list = karyawan_list.order_by('nama')
    elif selected_sort_by == 'jabatan':
        karyawan_list = karyawan_list.order_by('jabatan')
    elif selected_sort_by == 'role':
        karyawan_list = karyawan_list.order_by('user__role')
    elif selected_sort_by == 'status_keaktifan':
        karyawan_list = karyawan_list.order_by('status_keaktifan')

    # Pilihan kolom yang bisa ditampilkan
    available_columns = [
        ('nama', 'Nama'),
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

    # Tangkap aksi select_all/unselect_all dari query parameter
    select_action = request.GET.get('select_action')

    if select_action == 'select_all':
        selected_columns = [col[0] for col in available_columns]
    elif select_action == 'unselect_all':
        selected_columns = []
    else:
        selected_columns = request.GET.getlist('columns')

    # Kalau belum pernah pilih kolom apapun (misal user baru pertama kali buka), langsung tampilkan semua kolom
    if not selected_columns:
        selected_columns = [col[0] for col in available_columns]

    # Simpan ke session supaya pilihan kolom bertahan saat pindah page
    request.session['selected_columns'] = selected_columns

    # Paginasi
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
        # Bersihkan semua messages sisa (kalau ada)
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
                password='12345678',  # default password
                role=role
            )

            karyawan = form.save(commit=False)
            karyawan.user = user
            karyawan.save()

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
