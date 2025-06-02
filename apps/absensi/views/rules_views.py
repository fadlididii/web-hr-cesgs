from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from apps.authentication.decorators import role_required
from django.contrib import messages
from ..forms import RulesForm
from ..models import Rules

# Menampilkan daftar aturan absensi
@login_required
@role_required(['HRD'])
def list_rules(request):
    """Menampilkan daftar semua aturan absensi."""
    rules = Rules.objects.all()
    
    paginator = Paginator(rules, 10)  # Show 10 rules per page
    page_number = request.GET.get('page')
    rules = paginator.get_page(page_number)  # Get the current page's rules
    
    return render(request, 'absensi/rules/list.html', {'rules': rules})

# Menambahkan aturan absensi baru
@login_required
@role_required(['HRD'])
def create_rule(request):
    """Menambahkan aturan absensi baru."""
    if request.method == 'POST':
        form = RulesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Aturan absensi berhasil ditambahkan!")
            return redirect('list_rules')
    else:
        form = RulesForm()

    return render(request, 'absensi/rules/form.html', {'form': form, 'title': 'Tambah Aturan'})

# Mengedit aturan absensi yang sudah ada
@login_required
@role_required(['HRD'])
def update_rule(request, id):
    """Mengedit aturan absensi yang sudah ada."""
    rule = get_object_or_404(Rules, id_rules=id)
    if request.method == 'POST':
        form = RulesForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, "Aturan absensi berhasil diperbarui!")
            return redirect('list_rules')
    else:
        form = RulesForm(instance=rule)

    return render(request, 'absensi/rules/form.html', {'form': form, 'title': 'Edit Aturan'})

# Menghapus aturan absensi
@login_required
@role_required(['HRD'])
def delete_rule(request, id):
    """Menghapus aturan absensi."""
    rule = get_object_or_404(Rules, id_rules=id)
    rule.delete()
    messages.success(request, "Aturan absensi berhasil dihapus!")
    return redirect('list_rules')
