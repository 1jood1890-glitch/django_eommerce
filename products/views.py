from django.shortcuts import render, redirect, get_object_or_404
from .models import product
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import product 
from .forms import ContactForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import product, Order, Complaint 
from .forms import ContactForm




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


def product_details(request, pk):
 
    single_product = get_object_or_404(product, id=pk)
    
    context = {
        "product": single_product 
    }
    return render(request, "products/product_info.html", context)



def add_to_cart(request, pk):
    
    cart = request.session.get('cart', {})
    product_id = str(pk)
    
    
    action = request.GET.get('action') 

    if product_id in cart:
        if action == 'minus':

            cart[product_id] -= 1
            
            if cart[product_id] < 1:
                del cart[product_id]
        else:
            
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



def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # تحسين: إذا كان المستخدم مسجل، نحفظ في Complaint فقط ليظهر في بروفايله
            if request.user.is_authenticated:
                Complaint.objects.create(
                    user=request.user,
                    message=form.cleaned_data.get('message'),
                    is_resolved=False
                )
            else:
                # إذا كان زائراً (غير مسجل)، نحفظ في Contact للأدمن فقط
                form.save() 
            
            messages.success(request, 'تم استلام رسالتك وجاري معالجة الطلب.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

@login_required(login_url='login')
def profile_view(request):
    # تحسين: جلب الشكاوى والطلبات مرتبة من الأحدث (الأحدث فوق)
    user_complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'profile.html', {
        'user': request.user,
        'complaints': user_complaints,
        'orders': user_orders,         
    })

@login_required(login_url='login')
def checkout_view(request):
    cart = request.session.get('cart', {})
   
    if not cart:
        return redirect('list') 

    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        try:
            item_obj = product.objects.get(id=product_id) 
            item_total = item_obj.price * quantity
            total_price += item_total
            cart_items.append({
                'product': item_obj,
                'quantity': quantity,
                'total': item_total
            })
        except product.DoesNotExist:
            continue
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        customer_name = f"{first_name} {last_name}"
        
        # حفظ الطلب في موديل Order ليظهر في البروفايل والأدمن
        items_summary = ", ".join([f"{item['product'].name} (x{item['quantity']})" for item in cart_items])
        Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            total_price=total_price,
            items_summary=items_summary
        )
        
        context = {
            'customer_name': customer_name,
            'cart_items': cart_items,
            'total_price': total_price,
            'company_name': 'متجر سطر الإلكتروني',
            'tax_number': '300012345600003',
        }
        
        request.session['cart'] = {}
        request.session['cart_count'] = 0
        
        return render(request, 'invoice.html', context)

    return render(request, 'products/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


