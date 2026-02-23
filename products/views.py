from django.shortcuts import render, redirect, get_object_or_404
from .models import product

# دالة عرض قائمة المنتجات مع الفلترة والبحث
def list(request):
    # جلب المعايير من الرابط (الفئة والبحث)
    cat_id = request.GET.get("category_id")
    _search = request.GET.get("search")
    
    # جلب جميع المنتجات من قاعدة البيانات
    products = product.objects.all()
    page_title = "استكشف منتجاتنا"

    # الفلترة حسب القسم (تأكد أن الحقل في Models هو Category_id)
    if cat_id:
        products = products.filter(Category_id=cat_id)
        page_title = "منتجات القسم المختارة"

    # الفلترة حسب كلمة البحث
    if _search:
        products = products.filter(name__icontains=_search)
        page_title = f"نتائج البحث عن: {_search}"

    context = {
        "prod": products,   # يُستخدم في list.html
        "title": page_title,
    }
    return render(request, 'products/list.html', context)

# دالة عرض تفاصيل منتج معين بناءً على الرقم التعريفي (Primary Key)
def product_details(request, pk):
    # جلب المنتج أو إظهار صفحة 404 إذا كان المعرف غير صحيح
    single_product = get_object_or_404(product, id=pk)
    
    context = {
        "product": single_product # تم تغييره لـ product ليطابق القالب الخاص بك
    }
    return render(request, "products/product_info.html", context)

# دالة إضافة المنتج للسلة وتحديث العداد في الجلسة (Session)
def add_to_cart(request):
    # جلب القيمة الحالية للسلة أو البدء بـ 0
    counter = request.session.get('cart_count', 0)
    counter += 1
    request.session['cart_count'] = counter
    
    # البقاء في نفس الصفحة بعد الإضافة
    return redirect(request.META.get('HTTP_REFERER', '/'))