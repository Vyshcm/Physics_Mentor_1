from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .forms import SignupForm,LoginForm,ForgotPasswordForm,FeedbackForm,DoubtForm
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from .models import UserProfile,Feedback,Doubt

from django.db import IntegrityError

def index(request):
    return render(request,'index.html')

def signup(request):
    form=SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                UserProfile.objects.get_or_create(user=user, defaults={'role': 'Student', 'is_paid': False})
                messages.success(request, "Account created successfully!")
                return redirect('login') 
            except IntegrityError:
                form.add_error('username', 'This username is already taken. Please choose another.')
        
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
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Ensure profile exists for older users
    profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'Student'})
    
    if profile.role == 'Teacher':
        return render(request, 'accounts/teacher_dashboard.html')
    elif profile.role == 'Parent':
        return render(request, 'accounts/parent_dashboard.html')
    else: # Student
        return render(request, 'accounts/student_dashboard.html', {'is_paid': profile.is_paid})

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

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay

# PAYMENT VIEW
def payment(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    amount = 1999 * 100 # Razorpay takes amount in paise (₹1999)
    currency = "INR"
    
    # Check if keys are actually set or just placeholder
    is_mock = getattr(settings, 'RAZORPAY_KEY_ID', '').endswith('YOUR_KEY_HERE')
    
    context = {'is_mock': is_mock, 'amount': amount}
    
    if not is_mock:
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment_order = client.order.create(dict(amount=amount, currency=currency, payment_capture=1))
            context['order_id'] = payment_order['id']
            context['razorpay_key'] = settings.RAZORPAY_KEY_ID
        except Exception as e:
            # Fallback to mock if API key fails authentication with Razorpay server
            context['is_mock'] = True
            
    return render(request, 'accounts/payment.html', context)

@csrf_exempt
def payment_success(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == "POST":
        # Simulated payment directly updates profile
        profile = request.user.userprofile
        profile.is_paid = True
        from django.utils import timezone
        from datetime import timedelta
        # Set expiry date to 30 days from today
        profile.subscription_end_date = timezone.now().date() + timedelta(days=30)
        profile.save()
        messages.success(request, "Payment successful! You are now a premium user.")
        return redirect('dashboard')
        
    return redirect('dashboard')

@login_required
def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.save()
            messages.success(request, "Thanks! Your feedback was submitted.")
            return redirect('feedback')
    else:
        form = FeedbackForm()
    
    return render(request, 'accounts/feedback.html', {'form': form})

@login_required
def doubt_sessions_view(request):
    if request.method == "POST":
        form = DoubtForm(request.POST)
        if form.is_valid():
            doubt = form.save(commit=False)
            doubt.student = request.user
            doubt.save()
            messages.success(request, "Your doubt has been submitted successfully.")
            return redirect('doubt_sessions')
    else:
        form = DoubtForm()
    
    doubts = Doubt.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'accounts/doubt_sessions.html', {'form': form, 'doubts': doubts})