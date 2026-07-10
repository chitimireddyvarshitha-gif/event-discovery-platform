from django.contrib import admin
from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'registration_date')
    search_fields = ('user__username', 'user__email', 'event__event_name')
    list_filter = ('status', 'registration_date', 'event')
    date_hierarchy = 'registration_date'
