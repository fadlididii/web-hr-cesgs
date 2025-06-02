from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.hrd.models import Karyawan
from apps.authentication.models import User
from .forms import ProfilForm

@login_required
def profil_saya(request):
    user = request.user

    try:
        karyawan = Karyawan.objects.get(user=user)
    except Karyawan.DoesNotExist:
        messages.error(request, "Profil karyawan belum dibuat. Silakan hubungi HRD.")
        return redirect('home')

    if request.method == 'POST':
        form = ProfilForm(request.POST, instance=karyawan, user=user)

        if form.is_valid():
            # Email tidak boleh diubah: abaikan perubahan email dari form
            form.cleaned_data.pop('email', None)

            # Simpan data ke Karyawan
            form.save()

            messages.success(request, 'Profil berhasil diperbarui.')
            return redirect('profil_saya')
        else:
            messages.error(request, 'Terjadi kesalahan saat menyimpan profil.')
    else:
        form = ProfilForm(instance=karyawan, user=user)

    return render(request, 'profil/profil.html', {
        'form': form,
        'karyawan': karyawan,
        'user': user,
    })
