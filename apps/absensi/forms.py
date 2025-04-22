from django import forms
from .models import Rules
from datetime import datetime


BULAN_CHOICES = [(str(i), datetime(2024, i, 1).strftime('%B')) for i in range(1, 13)]

class UploadAbsensiForm(forms.Form):
    bulan = forms.ChoiceField(
        choices=BULAN_CHOICES,  # Menggunakan nama bulan
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tahun = forms.ChoiceField(
        choices=[(str(i), str(i)) for i in range(2020, 2031)],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    rules = forms.ModelChoiceField(
        queryset=Rules.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

class RulesForm(forms.ModelForm):
    class Meta:
        model = Rules
        fields = ['nama_rule', 'jam_masuk', 'jam_keluar', 'toleransi_telat', 'maksimal_izin']
        
        widgets = {
            'nama_rule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Aturan'}),
            'jam_masuk': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'jam_keluar': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'toleransi_telat': forms.NumberInput(attrs={'class': 'form-control'}),
            'maksimal_izin': forms.NumberInput(attrs={'class': 'form-control'}),
        }
