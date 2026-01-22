from django.shortcuts import render,redirect
from .forms import SignupForm,LoginForm,ForgotPasswordForm
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User

def index(request):
    return render(request,'index.html')
def signup(request):
    form=SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('login') 
        
    return render(request,'accounts/signup.html',{'form':form})

def Login(request):
    form=LoginForm()
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()    
            auth_login(request, user) 
            messages.success(request, "Logged in successfully!")
            return redirect('dashboard')
    return render(request,'accounts/login.html',{'form':form})

def dashboard(request):
    return render(request,'accounts/dashboard.html')

def logout(request):
    auth_logout(request)
    return redirect('login')

#FORGOT PASSWORD 

def forgotpassword(request):
    form = ForgotPasswordForm()

    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()

            messages.success(request, "Password reset successfully.")
            return redirect('login')

    return render(request, 'accounts/forgotpassword.html', {'form': form})