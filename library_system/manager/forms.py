from django import forms
from .models import Book, ManagerProfile

# ===============================
# 📘 Form thêm / sửa sách
# ===============================
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'year', 'category', 'description', 'total_copies', 'cover']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


# ===============================
# 👤 Form hồ sơ quản lý
# ===============================
class ManagerProfileForm(forms.ModelForm):
    class Meta:
        model = ManagerProfile
        fields = ['manager_code', 'email']
        labels = {
            'manager_code': 'Mã quản lý',
            'email': 'Email liên hệ',
        }
        widgets = {
            'manager_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập mã quản lý'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập email'
            }),
        }
