from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from core.models import *
from django.contrib import messages 
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm,PasswordResetForm,SetPasswordForm
import random 
from django.core.mail import send_mail
from .forms import UserRegisterForm

# Create your views here.
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('otp')
        messages.info(request,'Login failed...')
    return render(request,'accounts/login.html')
    
         

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            
            username = request.POST['username']
            email = request.POST['email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            request.session['username']=username
            request.session['password']=password1
            request.session['email']=email
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exists')
                return redirect('user_register')
            #elif User.objects.filter(email=email).exists():
                #messages.info(request, 'Email already exists')
                #return redirect('user_register')
            elif password1 != password2:
                messages.info(request, 'Passwords do not match')
                return redirect('user_register')
            else:
                # If everything is fine, save the user
                form.save()
                messages.success(request, 'Account created successfully')
                return redirect('user_login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('/')

def send_otp(request):
    otp=""
    for x in range(4):
        otp+=str(random.randint(0,9))
    
    request.session['otp']=otp
    print(request.session['otp'])
    
    user=request.user.email
    print(user)
    
    send_mail('otp for sign up', f'your OTP is:{otp}','svjoshi885@gmail.com',[user],fail_silently=False)
    return render(request,'accounts/otp.html')


def otp_verification(request):
    if request.method=='POST':
        otp_=request.POST.get('otp')
    if otp_ == request.session['otp']:

        #messages.info(request,'login successfully...')
        return redirect('index')
            
    else:
        messages.error(request,"otp doesn't match")
        return render(request,'accounts/otp.html')


def reset_password(request):
    if request.method == 'POST':
        user=request.POST['email']
    
        
        form=PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request,
                      use_https=request.is_secure(),
                      email_template_name='accounts/reset.html')
            
    else:
        form=PasswordResetForm()       
        return render(request,'accounts/reset.html',{'form':form})



def verify_email(request):
    if request.method=='POST':
        email=request.POST.get('email')
        request.session['email'] = email
        
        print(f"Submitted email:{email}")
        user = User.objects.get(email=email)
        print(user,'user..')
        
        if user:
            print('otp redirect page')
            messages.info(request,'Email verified')
            return redirect('otp1')
        else:
            messages.info(request,'Email does not match')
            return redirect('reset')
    else:
        return redirect('reset')
        
                
    
        

def set_password(request):
    user = User.objects.get(id=1) 
    if request.method == 'POST':
        form = SetPasswordForm(user=request.user,data=request.POST)
        if form.is_valid():
            print(form)
            form.save()
            return redirect('user_login') 
    else:
        form = SetPasswordForm(user=request.user)
    return render(request, 'accounts/set_password.html', {'form': form})

def reset_otp_verification(request):
    if request.method=='POST':
        otp1=request.POST.get('otp')
        if otp1 == request.session['otp']:
            return redirect('set_password')
            
    else:
        messages.error(request,"otp doesn't match")
        return render(request,'accounts/set_password.html')

def send_otp1(request):
    otp=""
    for x in range(4):
        otp+=str(random.randint(0,9))
    
    request.session['otp']=otp
    print(request.session['otp'])
    
    
    user=request.user.email
    print(user)
    send_mail('otp for sign up', f'your OTP is:{otp}','svjoshi885@gmail.com',[user],fail_silently=False)
    return render(request, 'accounts/otp1.html')

def changepass(request):
    if request.method=="POST":
        form = form = PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("user_login")
    else: 
        form = PasswordChangeForm(user=request.user)
    return render(request,'accounts/changepass.html',{'form':form})