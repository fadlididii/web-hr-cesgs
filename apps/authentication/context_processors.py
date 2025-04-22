def sidebar_menu(request):
    user = request.user
    sidebar = []

    if user.is_authenticated:
        if user.role == 'HRD':
            sidebar = [
                {'name': 'Dashboard', 'url': '/hrd/', 'icon': 'fa fa-home text-primary'},
                {'name': 'Upload Data Absensi', 'url': '/absensi/upload/', 'icon': 'ni ni-cloud-upload-96 text-info'},
                {'name': 'Manajemen Karyawan', 'url': '/hrd/manajemen-karyawan/', 'icon': 'ni ni-badge text-success'},
                {'name': 'Manajemen Rules', 'url': '/absensi/rules/', 'icon': 'ni ni-settings text-warning'},
                {
                    'name': 'Cuti',
                    'icon': 'ni ni-calendar-grid-58 text-warning',
                    'submenu': [
                        {'name': 'Approval Cuti', 'url': '/hrd/approval-cuti/', 'icon': 'fa fa-circle text-dark'},
                        {'name': 'Input Cuti Bersama', 'url': '/hrd/cuti-bersama/', 'icon': 'fa fa-circle text-dark'},
                        {'name': 'Jatah Cuti Karyawan', 'url': '/hrd/jatah-cuti/', 'icon': 'fa fa-circle text-dark'},
                        {'name': 'Pengajuan Cuti', 'url': '/karyawan/pengajuan-cuti/', 'icon': 'fa fa-circle text-dark'},
                        {'name': 'Tidak Ambil Cuti Bersama', 'url': '/karyawan/tidak-ambil-cuti/', 'icon': 'fa fa-circle text-dark'},
                    ]
                },
                {
                    'name': 'Izin',
                    'icon': 'ni ni-time-alarm text-info',
                    'submenu': [
                        {'name': 'Approval Izin', 'url': '/hrd/approval-izin/', 'icon': 'fa fa-circle text-dark'},
                        {'name': 'Pengajuan Izin', 'url': '/karyawan/pengajuan-izin/', 'icon': 'fa fa-circle text-dark'},
                    ]
                },
                {'name': 'Edit Profil', 'url': '/profil/', 'icon': 'ni ni-single-02 text-primary'},
            ]

        elif user.role == 'Karyawan Tetap':
            sidebar = [
                {'name': 'Dashboard', 'url': '/karyawan/', 'icon': 'fa fa-home text-primary'},
                {'name': 'Edit Profil', 'url': '/profil/', 'icon': 'ni ni-single-02 text-primary'},
                {
                    'name': 'Cuti',
                    'icon': 'ni ni-calendar-grid-58 text-warning',
                    'submenu': [
                        {'name': 'Pengajuan Cuti', 'url': '/karyawan/pengajuan-cuti/', 'icon': 'fa fa-circle text-dark'},
                        {'name': 'Tidak Ambil Cuti Bersama', 'url': '/karyawan/tidak-ambil-cuti/', 'icon': 'fa fa-circle text-dark'},
                    ]
                },
                {
                    'name': 'Izin',
                    'icon': 'ni ni-time-alarm text-info',
                    'submenu': [
                        {'name': 'Pengajuan Izin', 'url': '/karyawan/pengajuan-izin/', 'icon': 'fa fa-circle text-dark'},
                    ]
                },
            ]

        elif user.role == 'Magang':
            sidebar = [
                {'name': 'Edit Profil', 'url': '/profil/', 'icon': 'ni ni-single-02 text-primary'},
                {'name': 'Absensi', 'url': '/karyawan/absen-magang/', 'icon': 'ni ni-camera-compact text-danger'},
            ]

    return {'sidebar_menu': sidebar}
