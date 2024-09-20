from django.urls import path
from core import views


urlpatterns = [
    path('', views.index,name='index'),
    path('product_desc/<pk>', views.product_desc,name='product_desc'),
    path('add_to_cart/<pk>', views.add_to_cart,name='add_to_cart'),
    path('order_list', views.order_list,name='order_list'),
    path('add_item/<int:pk>', views.add_item,name='add_item'),
    path('remove_item/<int:pk>', views.remove_item,name='remove_item'),
    
    path('checkout_page/<int:id>', views.checkout_page,name='checkout_page'),
    path('orders', views.orders_view,name='orders'),
    
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('payment-confirm/<str:payment_intent_id>/<int:id>/', views.payment_confirm, name='payment_confirm'),
    path('confirm-payment/<int:id>/', views.confirm_payment, name='confirm_payment'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),
    path('search/', views.home, name='home'),
    path('add_category/', views.add_category, name='add_category'),
    path('orders/', views.all_orders, name='all_orders'),
]