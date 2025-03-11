from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.authentication.decorators import role_required

@login_required
@role_required(['Magang'])
def magang_dashboard(request):
    return render(request, 'magang/index.html')

@login_required
@role_required(['Magang'])
def edit_profil_magang(request):
    return render(request, 'magang/edit_profil.html')
