from django import forms
from apps.hrd.models import TidakAmbilCuti, CutiBersama

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
