from django.db import models
from category.models import Category
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class product(models.Model):
    name=models.CharField(max_length=50)
    price=models.DecimalField(max_digits=10,decimal_places=5)
    image_url=models.URLField(max_length=500)
    Category=models.ForeignKey(Category,on_delete=models.CASCADE)


    def __str__(self): 
        return self.name

class ProductDetail(models.Model):
    description=models.TextField()
    brand=models.CharField(max_length=100)
    stock=models.IntegerField(default=0)
    product=models.OneToOneField(product,on_delete=models.CASCADE,related_name='details')

    def __str__(self): 
        return self.brand

# --- كود الواجب ( رقم 11) ---

class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name="الاسم")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    subject = models.CharField(max_length=200, verbose_name="الموضوع")
    message = models.TextField(verbose_name="الرسالة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")

    def __str__(self):
        return f"رسالة من: {self.name}"
    

# جدول لحفظ الطلبات السابقة (لعرضها في البروفايل)
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=200)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    items_summary = models.TextField() # ملخص المنتجات
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"طلب رقم {self.id} - {self.customer_name}"

# جدول للشكاوى ورسائل الدعم
class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False) # هل تم الرد؟
    admin_reply = models.TextField(blank=True, null=True) # رد الإدارة
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"شكوى من {self.user.username}: {self.message[:20]}..."