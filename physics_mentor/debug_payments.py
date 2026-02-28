import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'physics_mentor.settings')
django.setup()

from accounts.models import Payment, User

print(f"Total Users: {User.objects.count()}")
print(f"Total Payments: {Payment.objects.count()}")

for p in Payment.objects.all():
    print(f"Payment ID: {p.id}, Student: {p.student.username}, Amount: {p.amount}, Date: {p.payment_date}")
