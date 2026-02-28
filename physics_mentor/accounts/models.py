from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
        ('Parent', 'Parent'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')
    student_class = models.CharField(max_length=20, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    subscription_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Feedback(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f"Feedback from {self.student.username} - {self.subject or 'No Subject'}"

class Doubt(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doubts')
    title = models.CharField(max_length=200, blank=True)
    question = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Doubt from {self.student.username}: {self.title or 'No Title'}"

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'userprofile__role': 'Student'}, related_name='linked_parents')
    parent_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Parent: {self.parent_name} (Student: {self.student.username})"

class ParentMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent_messages')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_parent_messages')
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from Parent {self.parent.username} regarding {self.student.username}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')
    payment_date = models.DateTimeField(auto_now_add=True)
    expiry_date_after_payment = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.student.username} ({self.status})"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.username} - {self.date}: {self.status}"

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    total_marks = models.IntegerField()
    duration_minutes = models.IntegerField(default=30)
    due_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    OPTION_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    marks = models.IntegerField(default=1)

    def __str__(self):
        return f"Q: {self.text[:50]}..."

class QuizResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}: {self.marks_obtained}/{self.quiz.total_marks}"

class Exam(models.Model):
    title = models.CharField(max_length=200)
    total_marks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ExamResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}: {self.marks_obtained}/{self.exam.total_marks}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    attachment = models.FileField(upload_to='assignments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Late', 'Late'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Submitted')

class Note(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='notes/')
    student_class = models.CharField(max_length=20, blank=True, null=True, help_text="Target class (Optional)")
    assigned_student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='personal_notes', help_text="Target specific student (Optional)")
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_notes')

    def __str__(self):
        return self.title

class LiveClass(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    meeting_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_live_classes')

    def __str__(self):
        return f"{self.title} - {self.date}"
