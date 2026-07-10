from django.contrib import admin
from .models import Event
from registrations.models import Registration


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ('user', 'registration_date')
    can_delete = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'organizer', 'category', 'date', 'venue', 'capacity')
    search_fields = ('event_name', 'venue', 'organizer__username')
    list_filter = ('category', 'date', 'organizer')
    inlines = [RegistrationInline]
