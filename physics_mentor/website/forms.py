from django import forms
from .models import ContactQuery

class ContactQueryForm(forms.ModelForm):
    class Meta:
        model = ContactQuery
        fields = "__all__"

        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Enter your full name"
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Enter your email address"
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Enter phone number",
                "id": "id_phone"
            }),
            "place": forms.TextInput(attrs={
                "placeholder": "Enter your city"
            }),
            "subject": forms.TextInput(attrs={
                "placeholder": "Physics"
            }),
            "message": forms.Textarea(attrs={
                "placeholder": "Write your message...",
                "rows": 4
            }),

             "country": forms.Select(),
             "student_class": forms.Select(),
             "tuition_type": forms.Select(),
        }
