from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'role', 'is_approved', 'is_staff')
    search_fields = ('username', 'full_name', 'email')
    list_filter = ('role', 'is_approved', 'is_staff')
    actions = ['approve_organizers']

    def approve_organizers(self, request, queryset):
        updated = queryset.filter(role='organizer').update(is_approved=True)
        self.message_user(request, f"{updated} organizer accounts have been successfully approved.")
    approve_organizers.short_description = "Approve selected organizer accounts"
