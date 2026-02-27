from django.contrib import admin
from .models import UserProfile, Feedback

admin.site.register(UserProfile)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'rating', 'status', 'created_at')
    list_filter = ('rating', 'status', 'created_at')
    search_fields = ('student__username', 'student__email', 'subject', 'message')
