from django.contrib import admin
from .models import product , ProductDetail, Contact, Order, Complaint 
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string 
from django.utils.html import strip_tags 

# تسجيل الموديلات الأساسية
admin.site.register(product)
admin.site.register(ProductDetail)

# --- واجب رقم 11: اتصل بنا ---
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
   
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_per_page = 20 

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_message', 'is_resolved', 'admin_reply', 'created_at') 
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('message', 'user__username', 'admin_reply')
    
    fields = ('user', 'message', 'is_resolved', 'admin_reply') 
    readonly_fields = ('user', 'message') 

    def short_message(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    short_message.short_description = 'نص الشكوى'


    def save_model(self, request, obj, form, change):
        if change and obj.admin_reply and obj.is_resolved:
            subject = 'تحديث بشأن استفسارك - متجر سطر'
            
            # تحضير البيانات لملف email_send.html
            context = {
                'username': obj.user.username,
                'user_message': obj.message,
                'admin_reply': obj.admin_reply,
            }
            
            # استدعاء القالب المنسق من مجلد emails
            html_message = render_to_string('emails/email_send.html', context)
            plain_message = strip_tags(html_message) # نسخة احتياطية نصية
            
            try:
                send_mail(
                    subject, 
                    plain_message, 
                    settings.EMAIL_HOST_USER, 
                    [obj.user.email], 
                    html_message=html_message 
                )
            except Exception as e:
                print(f"خطأ في إرسال الإيميل المنسق: {e}")
        
        super().save_model(request, obj, form, change)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer_name', 'items_summary', 'id')
    readonly_fields = ('user', 'customer_name', 'total_price', 'items_summary', 'created_at')