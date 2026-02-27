from django.contrib import admin
from .models import UserProfile, Feedback, Doubt
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
