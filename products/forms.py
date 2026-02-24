from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

# نموذج إنشاء الحساب المعدل
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="البريد الإلكتروني")

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # يسمح بالأحرف (الإنجليزية والعربية) والأرقام فقط
        # يمنع المسافات، والرموز مثل @ # $ % ^ & *
        if not re.match(r'^[\w\u0600-\u06FF]+$', username):
            raise ValidationError("اسم المستخدم يجب أن يحتوي على أحرف وأرقام فقط (بدون رموز أو مسافات).")
            
        return username

# نموذج تسجيل الدخول (يبقى كما هو أو يضاف له تحسينات الشكل)
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="اسم المستخدم", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم المستخدم'})
    )
    password = forms.CharField(
        label="كلمة المرور", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '******'})
    )