from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError


def validate_username_length(value, min_length=6):
    if len(value) < min_length:  # 7 because it should be more than 6 characters
        raise ValidationError('Tên tài khoản phải dài ít nhất 7 ký tự')


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label= ("Email"),
        validators=[validate_username_length],
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email của bạn',
            'required': 'required',
            'class': 'form-input',
        })
    )

    first_name = forms.CharField(
        label= ("Tên đầy đủ"),
        widget=forms.TextInput(attrs={
            'placeholder': 'Tên đầy đủ của bạn',
            'required': 'required',
            'minlength': '6',
            'maxlength': '50',
            'class': 'form-input',
        })
    )

    password1 = forms.CharField(
        label=("Mật khẩu"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mật khẩu của bạn',
            'required': 'required',
            'class': 'form-input',
        }),
    )   
    password2 = forms.CharField(
        label=("Xác nhận mật khẩu"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Xác nhận mật khẩu',
            'required': 'required',
            'class': 'form-input',
        }),
    )

    class Meta:
      model = User
      fields = ('username', 'first_name')


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label=("Tên đăng nhập"),
        widget=forms.TextInput(attrs={
            "placeholder": "Tên đăng nhập",
            'class': 'form-input'}))
    
    password = forms.CharField(
        label=("Mật khẩu"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Mật khẩu của bạn",
            'class': 'form-input'}))

    remember_me = forms.BooleanField(
        label='Ghi nhớ đăng nhập',
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "checkbox"}))
    
