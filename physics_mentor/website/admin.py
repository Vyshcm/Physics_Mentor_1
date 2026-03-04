from django.contrib import admin
from django.contrib.admin.models import LogEntry
from .models import ContactQuery


admin.site.register(LogEntry)
@admin.register(ContactQuery)
class ContactQueryAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "country",
        "phone",
        "email",
        "student_class",
        "tuition_type",
        "created_at",
    )
    list_filter = ("country", "student_class", "tuition_type", "created_at")
    search_fields = ("full_name", "phone", "email")
