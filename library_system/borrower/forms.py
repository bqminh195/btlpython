from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile
from manager.models import CheckRequest


# ========================
# 📦 FORM YÊU CẦU CHECK-IN / CHECK-OUT
# ========================
class CheckRequestForm(forms.ModelForm):
    class Meta:
        model = CheckRequest
        fields = ['check_type', 'reason']
        labels = {
            'check_type': 'Loại yêu cầu',
            'reason': 'Lý do',
        }
        widgets = {
            'check_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ========================
# 🧍 FORM ĐĂNG KÝ NGƯỜI DÙNG
# ========================
class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Tên đăng nhập",
        help_text="Chỉ bao gồm chữ cái, số và ký tự @/./+/-/_",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    msv = forms.CharField(
        label="Mã sinh viên",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=(
            "<ul>"
            "<li>Mật khẩu phải chứa ít nhất 8 ký tự.</li>"
            "<li>Không được quá giống với thông tin cá nhân.</li>"
            "<li>Không được là mật khẩu phổ biến.</li>"
            "<li>Không được hoàn toàn bằng số.</li>"
            "</ul>"
        )
    )
    password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Nhập lại mật khẩu để xác nhận."
    )

    class Meta:
        model = User
        fields = ["username", "email", "msv", "password1", "password2"]

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Mật khẩu xác nhận không khớp.")
        return cleaned_data


# ========================
# ✉️ CẬP NHẬT HỒ SƠ
# ========================
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]
        labels = {"email": "Địa chỉ Email"}
        widgets = {"email": forms.EmailInput(attrs={"class": "form-control"})}


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["msv"]
        labels = {"msv": "Mã sinh viên"}
        widgets = {"msv": forms.TextInput(attrs={"class": "form-control"})}


# ========================
# 🔐 ĐỔI MẬT KHẨU
# ========================
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Mật khẩu cũ",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    new_password1 = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text=(
            "<ul>"
            "<li>Mật khẩu phải chứa ít nhất 8 ký tự.</li>"
            "<li>Không được quá giống với thông tin cá nhân.</li>"
            "<li>Không được là mật khẩu phổ biến.</li>"
            "<li>Không được hoàn toàn bằng số.</li>"
            "</ul>"
        )
    )
    new_password2 = forms.CharField(
        label="Xác nhận mật khẩu mới",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Nhập lại mật khẩu mới để xác nhận."
    )
