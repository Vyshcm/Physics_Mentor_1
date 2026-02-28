from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordResetForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile, Feedback, Doubt, Assignment, Quiz, Payment, Exam, Question, Note, LiveClass


from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'username': 'Username',
            'email': 'Email',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

        for field_name, field in self.fields.items():
            field.label = ''                 # remove label
            field.help_text = None           # remove help text
            field.widget.attrs['placeholder'] = placeholders.get(field_name, '')

class LoginForm(AuthenticationForm):
    pass

# FORGOT PASSWORD FORM
class ForgotPasswordForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'})
    )
    password2 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise ValidationError("User does not exist")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2:
            if p1 != p2:
                raise ValidationError("Passwords do not match")

            validate_password(p1)

        return cleaned_data

class FeedbackForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    rating = forms.ChoiceField(choices=[('', 'Select Rating')] + RATING_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Feedback
        fields = ['subject', 'message', 'rating']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Subject (Optional)'}),
            'message': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Tell us what you think...', 'rows': 5}),
        }

class DoubtForm(forms.ModelForm):
    class Meta:
        model = Doubt
        fields = ['title', 'question']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Topic (Optional)'}),
            'question': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'What is your doubt?', 'rows': 5}),
        }

class StudentCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))
    class_name = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Class (e.g. 10th)'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email (Optional)'}),
        }

class ParentCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))
    student = forms.ModelChoiceField(queryset=User.objects.filter(userprofile__role='Student'), widget=forms.Select(attrs={'class': 'form-input'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username (Parent)'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
        }

class AssignmentCreationForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Assignment Title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Detailed instructions...', 'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }

class QuizCreationForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'total_marks', 'duration_minutes', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Quiz Title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Quiz Description...', 'rows': 3}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Total Marks'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Duration in minutes'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
        }

class QuestionCreationForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'marks']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Enter question text...', 'rows': 3}),
            'option_a': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Option D'}),
            'correct_option': forms.Select(attrs={'class': 'form-input'}),
            'marks': forms.NumberInput(attrs={'class': 'form-input'}),
        }

class RecordPaymentForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=User.objects.filter(userprofile__role='Student'), widget=forms.Select(attrs={'class': 'form-input'}))
    class Meta:
        model = Payment
        fields = ['student', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Amount (e.g. 1999)'}),
        }

class ExamCreationForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'total_marks']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Exam Title'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Total Marks'}),
        }

class AdminReplyForm(forms.Form):
    admin_reply = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Write your reply here...', 'rows': 4}))

class NoteForm(forms.ModelForm):
    assigned_student = forms.ModelChoiceField(
        queryset=User.objects.filter(userprofile__role='Student'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Specific Student (Optional)"
    )

    class Meta:
        model = Note
        fields = ['title', 'description', 'file', 'student_class', 'assigned_student']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Note Title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Description...', 'rows': 3}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'student_class': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Target Class (e.g. 10th)'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError("File size must be under 10MB.")
        return file

class LiveClassCreationForm(forms.ModelForm):
    class Meta:
        model = LiveClass
        fields = ['title', 'description', 'date', 'time', 'duration', 'meeting_link', 'audience_type', 'student_class', 'specific_students']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Class Title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Description...', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'duration': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Duration (mins)'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://zoom.us/j/...'}),
            'audience_type': forms.Select(attrs={'class': 'form-input', 'id': 'id_audience_type'}),
            'student_class': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 10th', 'id': 'id_student_class_input'}),
            'specific_students': forms.SelectMultiple(attrs={'class': 'form-input', 'id': 'id_specific_students_input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        audience_type = cleaned_data.get('audience_type')
        student_class = cleaned_data.get('student_class')
        specific_students = cleaned_data.get('specific_students')

        if audience_type == 'CLASS' and not student_class:
            self.add_error('student_class', "Please specify the target class.")
        
        if audience_type == 'STUDENTS' and not specific_students:
            self.add_error('specific_students', "Please select at least one student.")
            
        return cleaned_data