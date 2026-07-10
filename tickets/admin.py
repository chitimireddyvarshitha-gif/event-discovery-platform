from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'ticket_type', 'registration', 'issued_at')
    search_fields = ('ticket_code', 'registration__user__username', 'registration__event__event_name')
    list_filter = ('ticket_type', 'issued_at')
    date_hierarchy = 'issued_at'
