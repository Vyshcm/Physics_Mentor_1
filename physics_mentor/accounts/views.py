from django.shortcuts import render,redirect
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import SignupForm,LoginForm,ForgotPasswordForm,FeedbackForm,DoubtForm
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from .models import UserProfile, Feedback, Doubt, ParentProfile, ParentMessage, Payment, Attendance, Quiz, QuizResult, Exam, ExamResult, Assignment, AssignmentSubmission, Question, Note, LiveClass

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
            if user.is_staff or user.is_superuser:
                UserProfile.objects.get_or_create(user=user, defaults={'role': 'Teacher'})
                return redirect('teacher_dashboard')

            try:
                # 1. Parent Check
                if hasattr(user, 'parent_profile'):
                    return redirect('parent_dashboard')
                
                # 2. UserProfile Role Check
                profile = user.userprofile
                if profile.role == 'Teacher':
                    return redirect('teacher_dashboard')
                elif profile.role == 'Parent':
                    return redirect('parent_dashboard')
                else: # Student
                    return redirect('dashboard')
            except UserProfile.DoesNotExist:
                # Fallback: Students usually have profiles, others can go to dashboard to get one
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

    if request.user.is_staff or request.user.is_superuser or profile.role == 'Teacher':
        return redirect('teacher_dashboard')
    elif profile.role == 'Parent':
        return redirect('parent_dashboard')
    else: # Student
        # Calculate attendance %
        attendances = Attendance.objects.filter(student=request.user)
        total_days = attendances.count()
        attendance_pct = round((attendances.filter(status='Present').count() / total_days * 100), 1) if total_days > 0 else None
        
        # Fetch Live Classes & Notes
        live_classes = LiveClass.objects.filter(date__gte=timezone.now().date()).order_by('date', 'time')
        # Notes for student: (All) OR (their class) OR (specifically assigned to them)
        notes = Note.objects.filter(
            models.Q(student_class=profile.student_class) | 
            models.Q(student_class__in=['', None]) |
            models.Q(assigned_student=request.user)
        ).distinct().order_by('-created_at')

        return render(request, 'accounts/student_dashboard.html', {
            'is_paid': profile.is_paid,
            'attendance_pct': attendance_pct,
            'live_classes': live_classes,
            'notes': notes
        })

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
    
    # 6. Notes for student
    notes = Note.objects.filter(
        models.Q(student_class=student_profile.student_class) | 
        models.Q(student_class__in=['', None]) |
        models.Q(assigned_student=student)
    ).distinct().order_by('-created_at')

    # 7. Messaging Logic
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
        'notes': notes,
    }
    
    return render(request, 'accounts/parent_dashboard.html', context)

# --- Teacher/Admin Dashboard Views ---

def is_teacher(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'Teacher'))

def teacher_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not is_teacher(request.user):
            if request.user.is_authenticated:
                messages.error(request, "Access denied. You do not have teacher permissions.")
                return redirect('dashboard')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@teacher_required
def teacher_dashboard_view(request):
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    seven_days_later = today + timedelta(days=7)

    # Summary Stats
    total_students = UserProfile.objects.filter(role='Student').count()
    active_subscriptions = UserProfile.objects.filter(role='Student', is_paid=True).count()
    
    expiring_soon = UserProfile.objects.filter(
        role='Student', 
        is_paid=True, 
        subscription_end_date__range=[today, seven_days_later]
    ).count()
    
    unpaid_students = UserProfile.objects.filter(role='Student', is_paid=False).count()
    pending_doubts = Doubt.objects.filter(status='new').count()
    pending_messages = ParentMessage.objects.filter(status='new').count()

    context = {
        'total_students': total_students,
        'active_subscriptions': active_subscriptions,
        'expiring_soon': expiring_soon,
        'unpaid_students': unpaid_students,
        'pending_doubts': pending_doubts,
        'pending_messages': pending_messages,
    }
    return render(request, 'accounts/teacher_dashboard.html', context)

@teacher_required
def teacher_students_view(request):
    from .forms import StudentCreationForm, ParentCreationForm
    student_form = StudentCreationForm()
    parent_form = ParentCreationForm()

    if request.method == "POST":
        if "add_student" in request.POST:
            student_form = StudentCreationForm(request.POST)
            if student_form.is_valid():
                user = student_form.save(commit=False)
                user.set_password(student_form.cleaned_data['password'])
                user.save()
                UserProfile.objects.create(
                    user=user, 
                    role='Student', 
                    student_class=student_form.cleaned_data.get('class_name')
                )
                messages.success(request, f"Student {user.username} added successfully.")
                return redirect('teacher_students')
        
        elif "add_parent" in request.POST:
            parent_form = ParentCreationForm(request.POST)
            if parent_form.is_valid():
                user = parent_form.save(commit=False)
                user.set_password(parent_form.cleaned_data['password'])
                user.save()
                UserProfile.objects.create(user=user, role='Parent')
                ParentProfile.objects.create(
                    user=user,
                    student=parent_form.cleaned_data['student'],
                    parent_name=f"{user.first_name} {user.last_name}".strip() or user.username
                )
                messages.success(request, f"Parent account for {user.username} created and linked.")
                return redirect('teacher_students')

    # Search functionality
    query = request.GET.get('q', '')
    if query:
        students = UserProfile.objects.filter(role='Student', user__username__icontains=query).select_related('user')
    else:
        students = UserProfile.objects.filter(role='Student').select_related('user')
    
    return render(request, 'accounts/teacher_students.html', {
        'students': students, 
        'query': query,
        'student_form': student_form,
        'parent_form': parent_form
    })

@teacher_required
def teacher_attendance_view(request):
    from django.utils import timezone
    from django.db.models import Count, Q
    
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    today = timezone.now().date()

    if request.method == "POST":
        # Process attendance marking
        students = UserProfile.objects.filter(role='Student')
        for profile in students:
            status = request.POST.get(f'attendance_{profile.user.id}')
            remarks = request.POST.get(f'remarks_{profile.user.id}', '')
            if status:
                Attendance.objects.update_or_create(
                    student=profile.user,
                    date=selected_date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': request.user
                    }
                )
        messages.success(request, f"Attendance for {selected_date} updated successfully.")
        return redirect(f"{request.path}?date={date_str}")

    students = UserProfile.objects.filter(role='Student').select_related('user')
    attendance_records = Attendance.objects.filter(date=selected_date)
    attendance_dict = {a.student_id: {'status': a.status, 'remarks': a.remarks} for a in attendance_records}

    # Summary Stats for Today (or selected date)
    total_students = students.count()
    present_today = attendance_records.filter(status='Present').count()
    absent_today = attendance_records.filter(status='Absent').count()
    
    # Calculate Overall Attendance % (total across all time)
    all_attendance = Attendance.objects.all()
    total_records = all_attendance.count()
    total_present = all_attendance.filter(status='Present').count()
    overall_pct = round((total_present / total_records * 100), 1) if total_records > 0 else 0

    return render(request, 'accounts/teacher_attendance.html', {
        'students': students,
        'selected_date': selected_date,
        'today': today,
        'attendance_dict': attendance_dict,
        'total_students': total_students,
        'present_today': present_today,
        'absent_today': absent_today,
        'overall_pct': overall_pct,
    })

@teacher_required
def teacher_assignments_view(request):
    from .forms import AssignmentCreationForm
    form = AssignmentCreationForm()

    if request.method == "POST":
        if "create_assignment" in request.POST:
            form = AssignmentCreationForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Assignment created successfully.")
                return redirect('teacher_assignments')
        elif "delete_assignment" in request.POST:
            assignment_id = request.POST.get('assignment_id')
            Assignment.objects.filter(id=assignment_id).delete()
            messages.success(request, "Assignment deleted.")
            return redirect('teacher_assignments')

    assignments = Assignment.objects.all().order_by('-created_at')
    return render(request, 'accounts/teacher_assignments.html', {'assignments': assignments, 'form': form})

@teacher_required
def teacher_quizzes_view(request):
    from .forms import QuizCreationForm
    form = QuizCreationForm()

    if request.method == "POST":
        if "create_quiz" in request.POST:
            form = QuizCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Quiz created successfully.")
                return redirect('teacher_quizzes')
        elif "delete_quiz" in request.POST:
            quiz_id = request.POST.get('quiz_id')
            Quiz.objects.filter(id=quiz_id).delete()
            messages.success(request, "Quiz deleted.")
            return redirect('teacher_quizzes')

    quizzes = Quiz.objects.all().order_by('-created_at')
    return render(request, 'accounts/teacher_quizzes.html', {'quizzes': quizzes, 'form': form})

@teacher_required
def teacher_payments_view(request):
    from .forms import RecordPaymentForm
    from django.utils import timezone
    from datetime import timedelta
    
    form = RecordPaymentForm()
    if request.method == "POST":
        form = RecordPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.status = 'paid'
            
            # Update student profile
            student_profile = payment.student.userprofile
            student_profile.is_paid = True
            # Set expiry to 30 days from now
            expiry = timezone.now().date() + timedelta(days=30)
            student_profile.subscription_end_date = expiry
            student_profile.save()
            
            payment.expiry_date_after_payment = expiry
            payment.save()
            
            messages.success(request, f"Payment recorded for {payment.student.username}. Subscription extended to {expiry}.")
            return redirect('teacher_payments')

    # Fetch all payment transactions for history
    payments = Payment.objects.all().order_by('-payment_date').select_related('student')
    
    print(f"DEBUG: Total Payments found: {payments.count()}")
    
    context = {
        'payments': payments,
        'form': form,
    }
    return render(request, 'accounts/teacher_payments.html', context)

@teacher_required
def teacher_doubts_view(request):
    from .forms import AdminReplyForm
    from django.utils import timezone
    
    if request.method == "POST":
        doubt_id = request.POST.get('doubt_id')
        reply_text = request.POST.get('admin_reply')
        if doubt_id and reply_text:
            doubt = Doubt.objects.get(id=doubt_id)
            doubt.admin_reply = reply_text
            doubt.status = 'replied'
            doubt.replied_at = timezone.now()
            doubt.save()
            messages.success(request, f"Reply sent to {doubt.student.username}.")
            return redirect('teacher_doubts')

    doubts = Doubt.objects.all().order_by('-created_at').select_related('student')
    form = AdminReplyForm()
    return render(request, 'accounts/teacher_doubts.html', {'doubts': doubts, 'form': form})

@teacher_required
def teacher_parent_messages_view(request):
    from django.utils import timezone
    if request.method == "POST":
        message_id = request.POST.get('message_id')
        reply_text = request.POST.get('admin_reply')
        if message_id and reply_text:
            msg = ParentMessage.objects.get(id=message_id)
            msg.admin_reply = reply_text
            msg.status = 'replied'
            msg.replied_at = timezone.now()
            msg.save()
            messages.success(request, f"Reply sent to Parent {msg.parent.username}.")
            return redirect('teacher_parent_messages')

    messages_list = ParentMessage.objects.all().order_by('-created_at').select_related('parent', 'student')
    return render(request, 'accounts/teacher_parent_messages.html', {'messages_list': messages_list})
@teacher_required
def teacher_exams_view(request):
    from .forms import ExamCreationForm
    form = ExamCreationForm()

    if request.method == "POST":
        if "create_exam" in request.POST:
            form = ExamCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Exam created successfully.")
                return redirect('teacher_exams')
        elif "delete_exam" in request.POST:
            exam_id = request.POST.get('exam_id')
            Exam.objects.filter(id=exam_id).delete()
            messages.success(request, "Exam deleted.")
            return redirect('teacher_exams')

    exams = Exam.objects.all().order_by('-created_at')
    return render(request, 'accounts/teacher_exams.html', {'exams': exams, 'form': form})

@teacher_required
def student_performance_view(request, student_id):
    student = User.objects.get(id=student_id)
    
    quiz_results = QuizResult.objects.filter(student=student).select_related('quiz')
    exam_results = ExamResult.objects.filter(student=student).select_related('exam')
    attendance = Attendance.objects.filter(student=student).order_by('-date')
    submissions = AssignmentSubmission.objects.filter(student=student).select_related('assignment')
    
    # Calculate attendance percentage
    total_days = attendance.count()
    present_days = attendance.filter(status='Present').count()
    attendance_pct = round((present_days / total_days * 100), 1) if total_days > 0 else 0

    context = {
        'student': student,
        'quiz_results': quiz_results,
        'exam_results': exam_results,
        'attendance': attendance,
        'attendance_pct': attendance_pct,
        'submissions': submissions,
    }
    return render(request, 'accounts/student_performance.html', context)
from .models import Question

@teacher_required
def teacher_quiz_questions_view(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    from .forms import QuestionCreationForm
    form = QuestionCreationForm()

    if request.method == "POST":
        if "add_question" in request.POST:
            form = QuestionCreationForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.quiz = quiz
                question.save()
                messages.success(request, "Question added successfully.")
                return redirect("teacher_quiz_questions", quiz_id=quiz.id)
        elif "delete_question" in request.POST:
            question_id = request.POST.get("question_id")
            Question.objects.filter(id=question_id).delete()
            messages.success(request, "Question deleted.")
            return redirect("teacher_quiz_questions", quiz_id=quiz.id)

    questions = quiz.questions.all()
    return render(request, "accounts/teacher_quiz_questions.html", {
        "quiz": quiz,
        "questions": questions,
        "form": form
    })

@teacher_required
def teacher_quiz_toggle_publish(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    quiz.is_published = not quiz.is_published
    quiz.save()
    status = "Published" if quiz.is_published else "Unpublished"
    messages.success(request, f"Quiz {quiz.title} is now {status}.")
    return redirect("teacher_quizzes")

@teacher_required
def teacher_attendance_history_view(request):
    from django.db.models import Count, Q
    
    # Get all dates where attendance was marked, with summary counts
    history = Attendance.objects.values('date').annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='Present')),
        absent=Count('id', filter=Q(status='Absent'))
    ).order_by('-date')
    
    return render(request, 'accounts/teacher_attendance_history.html', {
        'history': history,
    })

@teacher_required
def teacher_student_attendance_report_view(request, student_id=None):
    from django.db.models import Count, Q
    
    students = UserProfile.objects.filter(role='Student').select_related('user')
    selected_student = None
    stats = None
    records = None
    
    if student_id:
        selected_student = User.objects.get(id=student_id)
    elif request.GET.get('student_id'):
        selected_student = User.objects.get(id=request.GET.get('student_id'))
        
    if selected_student:
        records = Attendance.objects.filter(student=selected_student).order_by('-date')
        total_days = records.count()
        present_count = records.filter(status='Present').count()
        absent_count = records.filter(status='Absent').count()
        percentage = round((present_count / total_days * 100), 1) if total_days > 0 else 0
        
        stats = {
            'total': total_days,
            'present': present_count,
            'absent': absent_count,
            'percentage': percentage,
        }
        # Last 10 records
        records = records[:10]

    return render(request, 'accounts/teacher_student_attendance_report.html', {
        'students': students,
        'selected_student': selected_student,
        'stats': stats,
        'records': records,
    })

@teacher_required
def teacher_notes_view(request):
    from .forms import NoteForm
    
    form = NoteForm()
    if request.method == "POST":
        if "upload_note" in request.POST:
            form = NoteForm(request.POST, request.FILES)
            if form.is_valid():
                note = form.save(commit=False)
                note.uploaded_by = request.user
                note.save()
                messages.success(request, "Note uploaded successfully.")
                return redirect('teacher_notes')

    # Summary Stats
    notes_list = Note.objects.all().order_by('-created_at')
    total_notes = notes_list.count()
    
    last_week = timezone.now() - timedelta(days=7)
    weekly_notes = notes_list.filter(created_at__gte=last_week).count()
    
    latest_note = notes_list.first()
    latest_date = latest_note.created_at if latest_note else None

    context = {
        'notes': notes_list,
        'form': form,
        'total_notes': total_notes,
        'weekly_notes': weekly_notes,
        'latest_date': latest_date,
    }
    return render(request, 'accounts/teacher_notes.html', context)

@teacher_required
def teacher_note_edit_view(request, note_id):
    from .forms import NoteForm
    note = Note.objects.get(id=note_id)
    form = NoteForm(instance=note)

    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated successfully.")
            return redirect('teacher_notes')

    return render(request, 'accounts/teacher_note_edit.html', {'form': form, 'note': note})

@teacher_required
def teacher_note_delete_view(request, note_id):
    note = Note.objects.get(id=note_id)
    if request.method == "POST":
        # Delete the file from storage
        if note.file:
            if os.path.exists(note.file.path):
                os.remove(note.file.path)
        note.delete()
        messages.success(request, "Note deleted successfully.")
        return redirect('teacher_notes')
    return redirect('teacher_notes')

@teacher_required
def teacher_live_classes_view(request):
    from .forms import LiveClassCreationForm
    form = LiveClassCreationForm()

    if request.method == "POST":
        if "create_class" in request.POST:
            form = LiveClassCreationForm(request.POST)
            if form.is_valid():
                live_class = form.save(commit=False)
                live_class.created_by = request.user
                live_class.save()
                messages.success(request, "Live class scheduled successfully.")
                return redirect('teacher_live_classes')
        elif "delete_class" in request.POST:
            class_id = request.POST.get('class_id')
            LiveClass.objects.filter(id=class_id).delete()
            messages.success(request, "Live class deleted successfully.")
            return redirect('teacher_live_classes')

    live_classes = LiveClass.objects.all().order_by('-date', '-time')
    return render(request, 'accounts/teacher_live_classes.html', {'live_classes': live_classes, 'form': form})
