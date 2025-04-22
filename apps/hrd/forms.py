from django import forms
from apps.hrd.models import Karyawan, Cuti, Izin, CutiBersama, TidakAmbilCuti
from apps.authentication.models import User

class KaryawanForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'pattern': r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$',
        'title': 'Gunakan format email yang valid, contoh: nama@email.com'
    }))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Karyawan
        fields = ['nama', 'nama_catatan_kehadiran', 'jabatan', 'divisi', 'alamat', 'status', 'mulai_kontrak', 'batas_kontrak', 'status_keaktifan', 'no_telepon']

        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': r'^[A-Za-z\s]+$',  # Hanya huruf dan spasi
                'title': 'Nama hanya boleh mengandung huruf dan spasi.'
            }),
            'nama_catatan_kehadiran': forms.TextInput(attrs={ 
                'class': 'form-control',
                'placeholder': 'Masukkan nama yang sesuai di catatan kehadiran'
            }),
            'jabatan': forms.TextInput(attrs={'class': 'form-control'}),
            'divisi': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'mulai_kontrak': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'batas_kontrak': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status_keaktifan': forms.Select(attrs={'class': 'form-control'}),
            'no_telepon': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': r'^(\+62|0)[0-9]{9,13}$',
                'title': 'Masukkan nomor telepon yang valid, contoh: +6281234567890 atau 081234567890'
            }),
        }
    
    def clean_nama(self):
        nama = self.cleaned_data.get('nama')
        if not nama:
            raise forms.ValidationError("Nama tidak boleh kosong.")
        
        # Preprocessing: Capitalize setiap kata
        nama_bersih = ' '.join(word.capitalize() for word in nama.split())
        return nama_bersih

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
        
class CutiBersamaForm(forms.ModelForm):
    class Meta:
        model = CutiBersama
        fields = ['tanggal', 'keterangan']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'keterangan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opsional'}),
        }
        
