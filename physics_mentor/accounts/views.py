from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .forms import SignupForm,LoginForm,ForgotPasswordForm,FeedbackForm,DoubtForm
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from .models import UserProfile, Feedback, Doubt, ParentProfile, ParentMessage, Payment, Attendance, Quiz, QuizResult, Exam, ExamResult, Assignment, AssignmentSubmission

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
            
            # Role-based redirect
            try:
                # 1. Parent Check (Priority)
                if hasattr(user, 'parent_profile'):
                    return redirect('parent_dashboard')
                
                # 2. Staff/Admin Check
                if user.is_staff:
                    return redirect('/admin/')

                # 3. UserProfile Role Check
                profile = user.userprofile
                if profile.role == 'Teacher':
                    return redirect('dashboard')
                elif profile.role == 'Parent':
                    return redirect('parent_dashboard')
                else: # Student
                    return redirect('dashboard')
            except UserProfile.DoesNotExist:
                # Fallback if profile missing
                if user.is_staff:
                    return redirect('/admin/')
                return redirect('dashboard')
    return render(request,'accounts/login.html',{'form':form})

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Ensure profile exists for older users
    profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'Student'})
    
    # Auto-detect parent role if ParentProfile exists
    if hasattr(request.user, 'parent_profile') and profile.role != 'Parent':
        profile.role = 'Parent'
        profile.save()

    if profile.role == 'Teacher':
        return render(request, 'accounts/teacher_dashboard.html')
    elif profile.role == 'Parent':
        return redirect('parent_dashboard')
    else: # Student
        return render(request, 'accounts/student_dashboard.html', {'is_paid': profile.is_paid})

def logout(request):
    # Consume existing messages to clear them before redirecting
    from django.contrib.messages import get_messages
    storage = get_messages(request)
    for message in storage:
        pass
    auth_logout(request)
    return redirect('home')

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
        expiry = timezone.now().date() + timedelta(days=30)
        profile.subscription_end_date = expiry
        profile.save()
        
        # ALSO create a Payment record for consistency
        from .models import Payment
        Payment.objects.create(
            student=request.user,
            amount=1999.00,
            status='paid',
            expiry_date_after_payment=expiry
        )

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

@login_required
def parent_dashboard_view(request):
    try:
        # Use select_related to get student in one query
        profile = ParentProfile.objects.select_related('student', 'student__userprofile').get(user=request.user)
    except ParentProfile.DoesNotExist:
        messages.error(request, "Parent profile not found. Please contact admin.")
        return redirect('login')
    
    student = profile.student
    student_profile = student.userprofile
    
    # 1. Payment Status Logic from real Payment history
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    
    # 1. Check real Payment history (Priority)
    latest_payment = Payment.objects.filter(student=student, status='paid').order_by('-payment_date').first()
    
    payment_status = "Not Paid"
    payment_class = "status-expired"
    subscription_end = None
    
    if latest_payment:
        payment_status = "Paid"
        payment_class = "status-paid"
        subscription_end = latest_payment.expiry_date_after_payment
        
        if subscription_end:
            if subscription_end >= today + timedelta(days=7):
                payment_status = "Paid"
                payment_class = "status-paid"
            elif today <= subscription_end < today + timedelta(days=7):
                payment_status = "Expiring Soon"
                payment_class = "status-warning"
            elif subscription_end < today:
                payment_status = "Expired"
                payment_class = "status-expired"
    else:
        # 2. Fallback to UserProfile if no explicit Payment record exists (e.g. for mock payments)
        if student_profile.is_paid:
            payment_status = "Paid"
            payment_class = "status-paid"
            subscription_end = student_profile.subscription_end_date
            
            if subscription_end:
                if subscription_end < today:
                    payment_status = "Expired"
                    payment_class = "status-expired"
                elif subscription_end < today + timedelta(days=7):
                    payment_status = "Expiring Soon"
                    payment_class = "status-warning"
    
    # 2. Performance Metrics
    quiz_results = QuizResult.objects.filter(student=student).select_related('quiz')
    if quiz_results.exists():
        total_pct = sum((r.marks_obtained / r.quiz.total_marks) * 100 for r in quiz_results)
        quiz_perf = round(total_pct / quiz_results.count(), 1)
    else:
        quiz_perf = None # None indicates "No records"
        
    exam_results = ExamResult.objects.filter(student=student).select_related('exam')
    if exam_results.exists():
        total_pct = sum((r.marks_obtained / r.exam.total_marks) * 100 for r in exam_results)
        exam_perf = round(total_pct / exam_results.count(), 1)
    else:
        exam_perf = None

    # 3. Attendance Metrics
    attendances = Attendance.objects.filter(student=student)
    total_days = attendances.count()
    if total_days > 0:
        present_days = attendances.filter(status='Present').count()
        attendance_pct = round((present_days / total_days) * 100, 1)
    else:
        attendance_pct = None

    # 4. Assignments Metrics
    total_assignments = Assignment.objects.all()
    submissions = AssignmentSubmission.objects.filter(student=student)
    
    submitted_ids = submissions.values_list('assignment_id', flat=True)
    pending_count = total_assignments.exclude(id__in=submitted_ids).count()
    
    assignments = {
        'submitted': submissions.filter(status='Submitted').count(),
        'pending': pending_count,
        'late': submissions.filter(status='Late').count()
    }
    
    # 5. Payment History - Explicitly query and log
    payment_history = list(Payment.objects.filter(student=student).order_by('-payment_date'))
    
    # Debug print to server console to verify data count
    print(f"DEBUG Dashboard: Found {len(payment_history)} real payments for student {student.username}")

    # Synthetic payment record if profile is paid but history is empty
    if not payment_history and student_profile.is_paid:
        print(f"DEBUG Dashboard: Using synthetic fallback for student {student.username}")
        payment_history = [{
            'amount': 1999.00,
            'status': 'paid',
            'payment_date': student_profile.subscription_end_date,
            'method': 'Direct Payment' # Fallback indicator
        }]
    else:
        # For real records, we might want to ensure they have a 'method' attribute or similar if template uses it
        # But we'll just use the objects as is.
        pass
    
    # 6. Messaging Logic
    if request.method == "POST" and "message_submit" in request.POST:
        msg_text = request.POST.get('message', '').strip()
        subject = request.POST.get('subject', '').strip()
        if msg_text:
            ParentMessage.objects.create(
                parent=request.user,
                student=student,
                subject=subject,
                message=msg_text
            )
            messages.success(request, "Your message has been sent to the mentor.")
            return redirect('parent_dashboard')
            
    messages_list = ParentMessage.objects.filter(parent=request.user).order_by('-created_at')
    
    context = {
        'profile': profile,
        'student': student,
        'student_profile': student_profile,
        'payment_status': payment_status,
        'payment_class': payment_class,
        'subscription_end': subscription_end,
        'quiz_perf': quiz_perf,
        'exam_perf': exam_perf,
        'attendance_pct': attendance_pct,
        'assignments': assignments,
        'payment_history': payment_history,
        'messages_list': messages_list,
    }
    
    return render(request, 'accounts/parent_dashboard.html', context)