from django.db import models

class ContactQuery(models.Model):

    COUNTRY_CHOICES = [
         ("", "Select Country"),   # 👈 important
        ("India", "India"),
        ("UAE (Dubai)", "UAE (Dubai)"),
        ("Oman", "Oman"),
        ("Qatar", "Qatar"),
        ("Saudi Arabia", "Saudi Arabia"),
        ("Kuwait", "Kuwait"),
        ("Bahrain", "Bahrain"),
        ("Other", "Other"),
    ]

    CLASS_CHOICES = [
         ("", "Select Class"),     # 👈 important
        ("Class 9", "Class 9"),
        ("Class 10", "Class 10"),
        ("Class 11", "Class 11"),
        ("Class 12", "Class 12"),
        ("Dropper", "Dropper"),
    ]

    TUITION_CHOICES = [
        ("", "Select Tuition Type"),  # 👈 important
        ("Online 1:1", "Online 1:1"),
        ("Online Group", "Online Group"),
        ("Crash Course", "Crash Course"),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    phone = models.CharField(max_length=25)   # ✅ international length
    student_class = models.CharField(max_length=20, choices=CLASS_CHOICES, blank=True, null=True)
    subject = models.CharField(max_length=50, default="Physics")
    place = models.CharField(max_length=80, blank=True, null=True)
    tuition_type = models.CharField(max_length=30, choices=TUITION_CHOICES, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.phone}"
