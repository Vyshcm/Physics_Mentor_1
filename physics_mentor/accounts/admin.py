from django.contrib import admin
from .models import UserProfile, Feedback, Doubt, ParentProfile, ParentMessage, Payment, Attendance, Quiz, QuizResult, Exam, ExamResult, Assignment, AssignmentSubmission
from django.utils import timezone

admin.site.register(UserProfile)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'rating', 'status', 'created_at')
    list_filter = ('rating', 'status', 'created_at')
    search_fields = ('student__username', 'student__email', 'subject', 'message')

@admin.register(Doubt)
class DoubtAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'status', 'created_at', 'replied_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__username', 'student__email', 'title', 'question', 'admin_reply')
    readonly_fields = ('created_at', 'updated_at', 'replied_at')
    
    def save_model(self, request, obj, form, change):
        if obj.admin_reply and not obj.replied_at:
            obj.status = 'replied'
            obj.replied_at = timezone.now()
        super().save_model(request, obj, form, change)

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('parent_name', 'user', 'student', 'created_at')
    search_fields = ('parent_name', 'user__username', 'student__username')

@admin.register(ParentMessage)
class ParentMessageAdmin(admin.ModelAdmin):
    list_display = ('parent', 'student', 'status', 'created_at', 'replied_at')
    list_filter = ('status', 'created_at')
    search_fields = ('parent__username', 'student__username', 'subject', 'message', 'admin_reply')
    readonly_fields = ('created_at', 'updated_at', 'replied_at')

    def save_model(self, request, obj, form, change):
        if obj.admin_reply and not obj.replied_at:
            obj.status = 'replied'
            obj.replied_at = timezone.now()
        super().save_model(request, obj, form, change)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'status', 'payment_date', 'expiry_date_after_payment')
    list_filter = ('status', 'payment_date')
    search_fields = ('student__username', 'student__email')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('student__username', 'student__email')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'total_marks', 'created_at')

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'marks_obtained', 'date_taken')
    list_filter = ('quiz', 'date_taken')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'total_marks', 'created_at')

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'date_taken')
    list_filter = ('exam', 'date_taken')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'due_date', 'created_at')

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'status')
    list_filter = ('status', 'submitted_at')
