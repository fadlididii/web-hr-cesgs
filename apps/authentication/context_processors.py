def sidebar_menu(request):
    user = request.user
    sidebar = []

    if user.is_authenticated:
        if user.role == 'HRD':
            sidebar = [
                {'name': 'Dashboard', 'url': '/hrd/', 'icon': 'fa fa-home text-primary text-primary'},
                {'name': 'Upload Data Absensi', 'url': '/hrd/upload-absensi/', 'icon': 'ni ni-cloud-upload-96 text-info'},
                {'name': 'Manajemen Karyawan', 'url': '/hrd/manajemen-karyawan/', 'icon': 'ni ni-badge text-success'},
                {'name': 'Approval Cuti', 'url': '/hrd/approval-cuti/', 'icon': 'ni ni-calendar-grid-58 text-warning'},
                {'name': 'Approval Izin', 'url': '/hrd/approval-izin/', 'icon': 'ni ni-check-bold text-danger'},
                {'name': 'Edit Profil', 'url': '/profil/', 'icon': 'ni ni-single-02 text-primary'},
                {'name': 'Pengajuan Izin', 'url': '/karyawan/pengajuan-izin/', 'icon': 'ni ni-send text-info'},
                {'name': 'Pengajuan Cuti', 'url': '/karyawan/pengajuan-cuti/', 'icon': 'ni ni-calendar-grid-58 text-warning'},
            ]
        elif user.role == 'Karyawan Tetap':
            sidebar = [
                {'name': 'Dashboard', 'url': '/karyawan/dashboard/', 'icon': 'fa fa-home text-primary text-primary'},
                {'name': 'Edit Profil', 'url': '/profil/', 'icon': 'ni ni-single-02 text-primary'},
                {'name': 'Pengajuan Izin', 'url': '/karyawan/pengajuan-izin/', 'icon': 'ni ni-send text-info'},
                {'name': 'Pengajuan Cuti', 'url': '/karyawan/pengajuan-cuti/', 'icon': 'ni ni-calendar-grid-58 text-warning'},
            ]
        elif user.role == 'Magang':
            sidebar = [
                {'name': 'Edit Profil', 'url': '/profil/', 'icon': 'ni ni-single-02 text-primary'},
                {'name': 'Absensi', 'url': '/karyawan/absen-magang/', 'icon': 'ni ni-camera-compact text-danger'},
            ]

    return {'sidebar_menu': sidebar}
