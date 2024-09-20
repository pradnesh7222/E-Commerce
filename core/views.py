from django.shortcuts import render,redirect,get_object_or_404
from core.forms import *
from django.contrib import messages
from core.models import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
import stripe
from core.models import OrderItem,Order
from django.core.mail import send_mail
from datetime import datetime
from .forms import SearchForm
from django.core.paginator import Paginator
from .stripe_utils import create_payment_intent
stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = 'http://localhost:8000'




# Create your views here.
def index(request):
    items = Product.objects.all().order_by('id')
    paginator = Paginator(items, 3)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)


    return render(request,'core/index.html',{'products':products})




def order_list(request):
    if Order.objects.filter(user=request.user,ordered=False).exists():
        order = Order.objects.get(user = request.user,ordered = False)
        return render(request,'core/order_list.html',{'order':order})
    return render(request,'core/order_list.html',{'message':"Your cart is empty"})
        

def product_desc(request,pk):
    product = Product.objects.get(pk=pk)
    images = product.img
    print(images,"images here")
    return render(request,'core/product_desc.html',{'product':product,"images":images})
    
def add_to_cart(request,pk):
    product = Product.objects.get(pk=pk)
    
    #Create Order item
    order_item, created = OrderItem.objects.get_or_create(
        product = product,
        user = request.user,
        ordered = False,
    )
     
    #get query set of order object of perticular user
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk = pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,"Added Quantity item..")
            return redirect('product_desc',pk=pk)
        else:
            order.items.add(order_item)
            messages.info(request,"Item Added to cart..")
            return redirect('product_desc',pk=pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"item added to cart")
        return redirect('product_desc',pk=pk)
    


def add_item(request,pk):
    
    product = Product.objects.get(pk=pk)  #get a perticuler Product of id = pk
    
    
    order_item, created = OrderItem.objects.get_or_create(
        product = product,
        user = request.user,
        ordered = False,
    )                                      #Create Order item
     
    
    order_qs = Order.objects.filter(user=request.user,ordered=False) #get query set of order object of perticular user
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk = pk).exists():
            if order_item.quantity < product.product_available_count:
                order_item.quantity += 1
                order_item.save()
                messages.info(request,"Added Quantity item..")
                return redirect('order_list')
            else:
                messages.info(request,"Sorry Product is out of stock")
                return redirect('order_list')
        else:
            order.items.add(order_item)
            messages.info(request,"Item Added to cart..")
            return redirect('product_desc',pk=pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"item added to cart")
        return redirect('product_desc',pk=pk)
      

def remove_item(request,pk):
    item = get_object_or_404(Product,pk=pk)
    order_qs = Order.objects.filter(
        user = request.user,
        ordered = False,
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk = pk).exists():
            order_item = OrderItem.objects.filter(
               product = item,
               user = request.user,
               ordered = False, 
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request,"Item quantity was updated")
            return redirect('order_list')
        else:
            messages.info(request,"This item is not in cart")
            return redirect('order_list')
    else:
        messages.info(request,'You do not have any order')
        return redirect('order_list')
    
def checkout_page(request,id):
    request.session['id']=id
    
    if CheckOutAddress.objects.filter(user=request.user).exists():
        return render(request,'core/checkout_address.html',{'payment_allow':'allow'})
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        try:
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip_code = form.cleaned_data.get('zip')
                
                checkout_address = CheckOutAddress(
                    user = request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    country = country,
                    zip_code = zip_code,
                )
                
                checkout_address.save()
                print('It should render the summary page')
                return render(request,'core/checkout_address.html',{'payment_allow':'allow'})
        except Exception as e:
            messages.warning(request,"Failed checkout")
            return redirect('checkout_page') 
    
    else:
        form = CheckoutForm()
        return render(request,'core/checkout_address.html',{'form':form})
    
 

 
 
    
@login_required
def orders_view(request):
    
    orders = Order.objects.filter(user=request.user, is_paid=True).prefetch_related('items__product')
    
    return render(request, 'core/user_orders.html', {'orders': orders})


def create_payment_intent(request):
    if request.method == 'GET':
        try:
            id = request.session['id']
            order = OrderItem.objects.get(id=id)  
            total_price = order.get_final_price()
            request.session['total_price']=total_price
            amount = total_price
            print(amount) 
            intent = stripe.PaymentIntent.create(
                amount=100,
                currency='usd',
                payment_method_types=['card'],
                payment_method="pm_card_visa",
                metadata={'order_id': id}
            )
            payment_intent_id = intent.id
            request.session['payment_intent_id']=payment_intent_id
            
            client_secret = intent.client_secret
            
            if intent and intent.client_secret:
                return redirect('payment_confirm',  payment_intent_id=payment_intent_id, id=id)
            else:
                return JsonResponse({'error': 'Failed to create PaymentIntent'}, status=400)
        
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)





def payment_confirm(request, payment_intent_id, id):
    return render(request, 'payment/payment_confirm.html', {'payment_intent_id': payment_intent_id, 'id': id})


@login_required(login_url='user_login')
def confirm_payment(request, id):
    if request.method == 'POST':
        
        payment_intent_id = request.session.get('payment_intent_id')
        print(payment_intent_id)
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            print(payment_intent)
            #if payment_intent status is already succeeded
            if payment_intent.status == 'requires_confirmation':
                payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
            if payment_intent.status == 'succeeded':
                
                payment_datetime = datetime.fromtimestamp(payment_intent.created)
                
                #create the Order
                order, created = Order.objects.get_or_create(
                    id=id,
                    defaults={
                        'user': request.user,
                        'ordered': True,
                        'order_id': payment_intent.id,
                        'datetime_ofpayment': payment_datetime,
                    }
                )
                print(order)
                if not created:
                    order.ordered = True
                    order.order_id = payment_intent.id
                    order.datetime_ofpayment = payment_datetime
                    order.save()
                
               
                order.items.clear()
                item = get_object_or_404(OrderItem, id=id)
                item.ordered = True
                item.save()
                order.items.add(item)
                print(item)
                
                #confirmation email
                total_price = request.session.get('total_price')
                subject = "Payment status"
                message = f"Order Confirmation \n\n Dear {order.user.username},\n Thank you for your order! We are delighted to inform you that your transaction hav been successfully completed. \n Order Summary: \n\n Total Amount - Rs {total_price:.2f} \n Order - { item.product.name } \n Quantity - { item.quantity } \n\n Your Order will be delivered in within next 3 days \n\n Thank you for shopping with us!\n Best regards,\n P-CART Customer Service"
                from_email = 'svjoshi885@gmail.com'
                recipient_list = [request.user.email]
                send_mail(subject, message, from_email, recipient_list)
                
                return render(request, 'payment/success.html', {'id': id})
            else:
                return render(request, 'payment/payment_failed.html', {'id': id})
                
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def home(request):
    form = SearchForm(request.GET or None)
    query = request.GET.get('query', '')
    
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    
    return render(request, 'core/index.html', {'form': form, 'products': products})


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
        
    else: 
        form = CategoryForm()
    return render(request, 'core/add_category.html', {'form': form})


def all_orders(request):
    orders = Order.objects.all()
    return render(request, 'core/orders.html', {'orders': orders})

def payment_failed(request):
    return render(request,'payment/payment_failed.html')