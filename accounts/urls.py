from django.urls import path
from accounts import views

urlpatterns = [
    path('user_login',views.user_login,name='user_login'),
    path('user_register',views.user_register,name='user_register'),
    path('user_logout',views.user_logout,name='user_logout'),
    
    path('reset/',views.reset_password,name='reset'),
    path('otp/',views.send_otp,name='otp'),
    path('otp_verification/',views.otp_verification,name='verification'),
    path('otp_verification1/',views.reset_otp_verification,name='otp_reset_verification'),
    path('email_verification/',views.verify_email,name='email_verification'),
    path('otp1/',views.send_otp1,name='otp1'),
    path('set_new_pass/',views.set_password,name='set_password'),
    
    path('changepass/',views.changepass,name='change_pass'),
    
]
