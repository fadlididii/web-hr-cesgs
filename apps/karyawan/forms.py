from django import forms
from apps.hrd.models import TidakAmbilCuti, CutiBersama, Cuti, Izin, CutiBersama, TidakAmbilCuti

class TidakAmbilCutiForm(forms.ModelForm):
    tanggal = forms.ModelMultipleChoiceField(
        queryset=CutiBersama.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True,
        label='Tanggal Tidak Ambil Cuti'
    )

    class Meta:
        model = TidakAmbilCuti
        fields = ['tanggal', 'alasan', 'file_pengajuan']
        widgets = {
            'alasan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file_pengajuan': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file_pengajuan'].required = True
        self.fields['alasan'].label = 'Job Desc'

class CutiForm(forms.ModelForm):
    class Meta:
        model = Cuti
        fields = ['jenis_cuti', 'tanggal_mulai', 'tanggal_selesai', 'file_pengajuan', 'file_dokumen_formal']
        widgets = {
            'jenis_cuti': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'file_pengajuan': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
            'file_dokumen_formal': forms.ClearableFileInput(attrs={'class': 'form-control'}), 
        }
        
    def __init__(self, *args, **kwargs):
        super(CutiForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

class IzinForm(forms.ModelForm):
    class Meta:
        model = Izin
        fields = ['jenis_izin', 'tanggal_izin', 'alasan', 'file_pengajuan']
        widgets = {
            'jenis_izin': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_izin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'alasan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file_pengajuan': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file_pengajuan'].label = 'Upload Bukti SS Ke Atasan Langsung'
        
