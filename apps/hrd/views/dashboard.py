from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.authentication.decorators import role_required

@login_required
@role_required(['HRD'])
def hrd_dashboard(request):
    return render(request, 'hrd/index.html')
