from django.contrib import admin
from .models import product , ProductDetail, Contact, Order, Complaint 

admin.site.register(product)
admin.site.register(ProductDetail)


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
    readonly_fields = ('user', 'message', 'created_at') 

    def short_message(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    short_message.short_description = 'نص الشكوى'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer_name', 'items_summary', 'id')
    readonly_fields = ('user', 'customer_name', 'total_price', 'items_summary', 'created_at') # منع تعديل الطلبات لضمان النزاهة المالية