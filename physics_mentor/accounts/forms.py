from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordResetForm
from django.contrib.auth.models import User
from django import forms
from .models import Feedback, Doubt
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