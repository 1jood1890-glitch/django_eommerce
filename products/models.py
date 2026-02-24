from django.db import models
from category.models import Category

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