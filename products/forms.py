from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Contact  # أضفنا هذا السطر لاستيراد المودل الجديد ( للواجب)

# --- نموذج إنشاء الحساب ---
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="البريد الإلكتروني")

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_username(self):
        username = self.cleaned_data.get('username')
       
        if not re.match(r'^[\w\u0600-\u06FF]+$', username):
       
            raise ValidationError("اسم المستخدم يجب أن يحتوي على أحرف وأرقام فقط (بدون رموز أو مسافات).")
       
        return username

# --- نموذج تسجيل الدخول ---
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="اسم المستخدم", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم المستخدم'})
    )
    password = forms.CharField(
        label="كلمة المرور", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '******'})
    )

class ContactFormOld(forms.Form): 
    name = forms.CharField(
        label="الاسم",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ادخل اسمك'
        })
    )

    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ادخل بريدك الإليكتروني'
        })
    )

    subject = forms.CharField(
        label="الموضوع",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ادخل عنوان الرسالة'
        })
    )

    message = forms.CharField(
        label="الرسالة",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'ادخل محتوى الرسالة'
        })
    )

# ملاحظة: الكود أدناه هو المطلوب في (التمرين رقم 11)
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact  
        fields = ['name', 'email', 'subject', 'message']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ادخل اسمك'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ادخل بريدك الإليكتروني'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ادخل عنوان الرسالة'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'ادخل محتوى الرسالة'}),
        }
        
        
        labels = {
            'name': 'الاسم',
            'email': 'البريد الإلكتروني',
            'subject': 'الموضوع',
            'message': 'الرسالة',
        }
