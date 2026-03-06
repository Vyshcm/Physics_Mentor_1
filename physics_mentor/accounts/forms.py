from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordResetForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile, Feedback, Doubt, Assignment, AssignmentSubmission, Quiz, Payment, Exam, Question, Note, LiveClass, ExamSubmission


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

        self.fields['standard'] = forms.ChoiceField(
            choices=[('', 'Select your Class')] + UserProfile.STANDARD_CHOICES,
            required=True,
            widget=forms.Select(attrs={'class': 'form-input'})
        )

        for field_name, field in self.fields.items():
            if field_name != 'standard':
                field.label = ''                 # remove label
                field.help_text = None           # remove help text
                field.widget.attrs['placeholder'] = placeholders.get(field_name, '')
            else:
                field.label = ''

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
    rating = forms.ChoiceField(choices=[('', 'Select Rating')] + RATING_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Feedback
        fields = ['rating', 'message']
        widgets = {
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
    standard = forms.ChoiceField(
        choices=[('', 'Select Class')] + UserProfile.STANDARD_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
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
        fields = ['title', 'description', 'due_date', 'attachment', 'standard']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Assignment Title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Detailed instructions...', 'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'standard': forms.Select(attrs={'class': 'form-input'}),
        }

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }

class ExamSubmissionForm(forms.ModelForm):
    class Meta:
        model = ExamSubmission
        fields = ['answer_file']
        widgets = {
            'answer_file': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }

    def clean_answer_file(self):
        file = self.cleaned_data.get('answer_file')
        if file:
            if file.size > 100 * 1024 * 1024:  # 100MB
                raise ValidationError("File size must be under 100MB.")
        return file

class QuizCreationForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'total_marks', 'duration_minutes', 'start_time', 'due_date', 'standard']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Quiz Title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Quiz Description...', 'rows': 3}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Total Marks'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Duration in minutes'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'standard': forms.Select(attrs={'class': 'form-input'}),
        }

class QuestionCreationForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'marks']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': r'Enter question text... (Use \(...\) for inline and \[...\] for block physics formulas)', 'rows': 4}),
            'option_a': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Option A (You can use math symbols here)', 'rows': 2}),
            'option_b': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Option B', 'rows': 2}),
            'option_c': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Option C', 'rows': 2}),
            'option_d': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Option D', 'rows': 2}),
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
    CLASS_CHOICES = [
        (10, 'Class 10'),
        (11, 'Class 11'),
        (12, 'Class 12'),
    ]
    target_class = forms.ChoiceField(
        choices=[('', 'Select Target Class')] + CLASS_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Target Class"
    )

    class Meta:
        model = Exam
        fields = ['title', 'target_class', 'exam_date', 'start_time', 'duration_minutes', 'description', 'question_file', 'exam_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Exam Title / Chapter Name'}),
            'exam_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Duration in minutes (optional)'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Short description / instructions (optional)', 'rows': 3}),
            'question_file': forms.ClearableFileInput(attrs={'class': 'form-input', 'accept': '.pdf,.doc,.docx'}),
            'exam_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://meet.google.com/...'}),
        }
        labels = {
            'exam_link': 'Exam Link (Join Exam / Camera URL)',
            'question_file': 'Upload Question Paper (PDF/DOC)',
        }

    def clean_target_class(self):
        val = self.cleaned_data.get('target_class')
        if not val:
            raise forms.ValidationError("Please select a target class.")
        return int(val)

    def clean_question_file(self):
        f = self.cleaned_data.get('question_file')
        if not f:
            raise forms.ValidationError("Question paper file is required.")
        return f

    def clean_exam_link(self):
        link = self.cleaned_data.get('exam_link', '').strip()
        if not link:
            raise forms.ValidationError("Exam link is required.")
        return link

class AdminReplyForm(forms.Form):
    admin_reply = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Write your reply here...', 'rows': 4}))

class NoteForm(forms.ModelForm):
    standard = forms.ChoiceField(
        choices=[('', 'Select Class')] + UserProfile.STANDARD_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Target Class"
    )
    assigned_student = forms.ModelChoiceField(
        queryset=User.objects.filter(userprofile__role='Student'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Specific Student (Optional)"
    )

    class Meta:
        model = Note
        fields = ['title', 'description', 'file', 'standard', 'assigned_student']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Note Title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Description...', 'rows': 3}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-input', 'id': 'fileInput', 'style': 'display: none;'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 100 * 1024 * 1024:  # 100MB
                raise ValidationError("File size must be under 100MB.")
        return file

class LiveClassCreationForm(forms.ModelForm):
    target_class = forms.ChoiceField(
        choices=[('', 'Select Class'), (10, 'Class 10'), (11, 'Class 11'), (12, 'Class 12')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_target_class_input'})
    )

    class Meta:
        model = LiveClass
        fields = ['title', 'description', 'date', 'time', 'duration', 'meeting_link', 'audience_type', 'target_class', 'specific_students']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Class Title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Description...', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'duration': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Duration (mins)'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://zoom.us/j/...'}),
            'audience_type': forms.Select(attrs={'class': 'form-input', 'id': 'id_audience_type'}),
            'specific_students': forms.SelectMultiple(attrs={'class': 'form-input', 'id': 'id_specific_students_input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        audience_type = cleaned_data.get('audience_type')
        target_class = cleaned_data.get('target_class')
        specific_students = cleaned_data.get('specific_students')

        if audience_type == 'CLASS':
            if not target_class:
                self.add_error('target_class', "Please select a class.")
            # Clear other audience fields
            cleaned_data['specific_students'] = []
        elif audience_type == 'ALL':
            cleaned_data['target_class'] = None
            cleaned_data['specific_students'] = []
        elif audience_type == 'STUDENTS':
            if not specific_students:
                self.add_error('specific_students', "Please select at least one student.")
            cleaned_data['target_class'] = None
            
        return cleaned_data