from django.shortcuts import redirect
from apps.hrd.models import Karyawan

class CheckKaryawanStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                karyawan = Karyawan.objects.get(user=request.user)
                if karyawan.status_keaktifan == 'Tidak Aktif':
                    from django.contrib.auth import logout
                    logout(request)
                    return redirect('login')  # Redirect ke login dengan pesan
            except Karyawan.DoesNotExist:
                pass
        return self.get_response(request)
