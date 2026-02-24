from django.shortcuts import render, redirect, get_object_or_404
from .models import product
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

# دالة عرض قائمة المنتجات مع الفلترة والبحث (كما هي)
def list(request):
  
    cat_id = request.GET.get("category_id")
 
    _search = request.GET.get("search")
  
    products = product.objects.all()
    page_title = "استكشف منتجاتنا"



    if cat_id:
        products = products.filter(Category_id=cat_id)
        page_title = "منتجات القسم المختارة"


    if _search:
        products = products.filter(name__icontains=_search)
        page_title = f"نتائج البحث عن: {_search}"

    context = {
        "prod": products,
        "title": page_title,
    }
    return render(request, 'products/list.html', context)

# دالة عرض تفاصيل منتج معين (كما هي)
def product_details(request, pk):
 
    single_product = get_object_or_404(product, id=pk)
    
    context = {
        "product": single_product 
    }
    return render(request, "products/product_info.html", context)

# --- الدوال المعدلة لإدارة السلة والكميات ---

def add_to_cart(request, pk):
    # جلب السلة الحالية
    cart = request.session.get('cart', {})
    product_id = str(pk)
    
    # جلب نوع العملية (زيادة أو نقصان) من الرابط
    action = request.GET.get('action') 

    if product_id in cart:
        if action == 'minus':
            # تقليل الكمية
            cart[product_id] -= 1
            # حذف المنتج إذا وصلت الكمية لصفر
            if cart[product_id] < 1:
                del cart[product_id]
        else:
            # زيادة الكمية (الحالة الافتراضية)
            cart[product_id] += 1
    else:
        
        if action != 'minus':
            cart[product_id] = 1
        
    
    request.session['cart'] = cart
    request.session['cart_count'] = sum(cart.values())
    
    # الرجوع لآخر صفحة كان فيها العميل
    return redirect(request.META.get('HTTP_REFERER', 'cart_view'))

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        item = get_object_or_404(product, id=product_id)
        item_total = item.price * quantity
        total_price += item_total
        
        cart_items.append({
            'product': item,
            'quantity': quantity,
            'total': item_total
        })
        
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'products/cart.html', context)

def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    product_id = str(pk)
    if product_id in cart:
        del cart[product_id]
    request.session['cart'] = cart
    request.session['cart_count'] = sum(cart.values())
    return redirect('cart_view')

def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
        request.session['cart_count'] = 0
    return redirect('cart_view')

# --- دوال المصادقة (الحسابات) ---

def auth_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('list')
    else:
        form = RegisterForm()
    return render(request, 'accounts/auth_register.html', {'form': form})

def auth_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            return redirect(request.GET.get('next', 'list'))
    else:
        form = LoginForm()
    return render(request, 'accounts/auth_login.html', {'form': form})

def auth_logout(request):
    logout(request)
    return redirect('list')



@login_required(login_url='login')
def checkout_view(request):
    cart = request.session.get('cart', {})
    
    
    if not cart:
        return redirect('cart_view')
    
    
    if request.method == 'POST':
        
        
        request.session['cart'] = {}
        request.session['cart_count'] = 0
        return render(request, 'products/success.html')

    
    cart_items = []
    total_price = 0
    for product_id, quantity in cart.items():
        item = get_object_or_404(product, id=product_id)
        item_total = item.price * quantity
        total_price += item_total
        cart_items.append({
            'product': item,
            'quantity': quantity,
            'total': item_total
        })
        
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'products/checkout.html', context)



def contact(request):
    if request.method == 'POST':
        # استقبال البيانات من الفورم
        form = ContactForm(request.POST)
        
        if form.is_valid():
            
            # ملاحظة: السطر أدناه هو المطلوب في (واجب رقم 11)
            
            form.save() 
            
            messages.success(request, 'تم إرسال رسالتك بنجاح! تم حفظ بياناتك في قاعدة البيانات.')
            
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

