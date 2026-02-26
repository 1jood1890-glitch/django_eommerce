from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

# 3. مكتبات الإيميل والقوالب (Email & Templates)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from .models import product, Order, Complaint

from .forms import RegisterForm, LoginForm, ContactForm
import qrcode
import base64
from io import BytesIO


# --- دوال عرض المنتجات والسلة ---

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
    return render(request, "products/product_info.html", {"product": single_product})

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
  
    return redirect(request.META.get('HTTP_REFERER', 'cart_view'))

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []

    total_price = 0
  
    for product_id, quantity in cart.items():
        item = get_object_or_404(product, id=product_id)
        item_total = item.price * quantity
        total_price += item_total
        cart_items.append({'product': item, 'quantity': quantity, 'total': item_total})
        
    return render(request, 'products/cart.html', {'cart_items': cart_items, 'total_price': total_price})

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

# --- دوال الحسابات والشكاوى ---

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
       
            if request.user.is_authenticated:
                Complaint.objects.create(
                    user=request.user,
                    message=form.
                    cleaned_data.get('message'),
                    is_resolved=False
                )
            else:
        
                form.save() 
           
            messages.success(request, 'تم استلام رسالتك وجاري معالجة الطلب.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


@login_required(login_url='login')
def profile_view(request):
    
    user_complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'profile.html', {
        'user': request.user,
        'complaints': user_complaints,
        'orders': user_orders,         
    })



def send_invoice_email(order):
    subject = f'فاتورة شراء رقم #{order.id} - متجر سطر'
    context = {
        'customer_name': order.customer_name,
        'order_id': order.id,
        'items': order.items_summary,
        'total': order.total_price,
        'date': order.created_at.strftime('%Y-%m-%d %H:%M'),
    }
    html_message = render_to_string('emails/invoice_send.html', context)
    plain_message = strip_tags(html_message)
    try:
        send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [order.user.email], html_message=html_message)
    except Exception as e:
        print(f"خطأ في إرسال الفاتورة: {e}")

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
            cart_items.append({'product': item_obj, 'quantity': quantity, 'total': item_total})
        except product.DoesNotExist:
            continue
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        customer_name = f"{first_name} {last_name}"
        items_summary = ", ".join([f"{item['product'].name} (x{item['quantity']})" for item in cart_items])
        
        # 1. إنشاء الطلب
        new_order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            total_price=total_price,
            items_summary=items_summary
        )

        # 2. إرسال الفاتورة للإيميل
        send_invoice_email(new_order)

        # 3. توليد الـ QR Code ببيانات نصية واضحة
        company_name = 'متجر سطر الإلكتروني'
        tax_number = '300012345600003'
        
        # هذا هو النص الذي سيظهر عند مسح الباركود
        qr_text = (
            f"اسم المتجر: {company_name}\n"
            f"الرقم الضريبي: {tax_number}\n"
            f"العميل: {customer_name}\n"
            f"المبلغ الإجمالي: {total_price} ر.س\n"
            f"التاريخ: {new_order.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        
        # إعدادات الـ QR لضمان القراءة السهلة
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_str = base64.b64encode(buffer.getvalue()).decode()
        
        #  إرسال البيانات للصفحة
        context = {
            'customer_name': customer_name,
            'cart_items': cart_items,
            'total_price': total_price,
            'company_name': company_name,
            'tax_number': tax_number,
            'qr_code': qr_str, 
            'order_date': new_order.created_at,
        }

        
        request.session['cart'] = {}
      
        request.session['cart_count'] = 0
        
        return render(request, 'invoice.html', context)

    return render(request, 'products/checkout.html', {'cart_items': cart_items, 'total_price': total_price})
    
    # if request.method == 'POST':
    #     first_name = request.POST.get('first_name', '')
    #     last_name = request.POST.get('last_name', '')
    #     customer_name = f"{first_name} {last_name}"
     
    #     items_summary = ", ".join([f"{item['product'].name} (x{item['quantity']})" for item in cart_items])
        
    #     # حفظ الطلب وإرسال الإيميل
    #     new_order = Order.objects.create(
    #         user=request.user,
    #         customer_name=customer_name,
    #         total_price=total_price,
    #         items_summary=items_summary
    #     )
    #     send_invoice_email(new_order)
        
    #     context = {
    #         'customer_name': customer_name,
    #         'cart_items': cart_items,
    #         'total_price': total_price,
    #         'company_name': 'متجر سطر الإلكتروني',
    #         'tax_number': '300012345600003',
    #     }
       
    #     request.session['cart'] = {}
       
    #     request.session['cart_count'] = 0
       
    #     return render(request, 'invoice.html', context)

    # return render(request, 'products/checkout.html', {'cart_items': cart_items, 'total_price': total_price})
