from django.contrib import admin
from .models import product , ProductDetail, Contact # أضفنا Contact هنا

# Register your models here.

admin.site.register(product)
admin.site.register(ProductDetail)

# ملاحظة: الكود أدناه هو المطلوب في (التمرين رقم 11)
# تسجيل مودل Contact ليعرض البيانات المخزنة بطريقة الـ select في لوحة التحكم
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    # عرض الحقول في جدول لوحة التحكم لسهولة التأكد من البيانات
    list_display = ('name', 'email', 'subject', 'created_at')
    # إضافة إمكانية البحث بالاسم أو الإيميل
    search_fields = ('name', 'email')
