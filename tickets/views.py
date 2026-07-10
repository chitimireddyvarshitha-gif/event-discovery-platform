from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from events.models import Event

from .models import Ticket


@login_required
def ticket_list(request):
    """Show tickets belonging to the logged-in attendee."""
    tickets = Ticket.objects.filter(registration__user=request.user).select_related('registration__event')
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


@login_required
def ticket_detail(request, ticket_id):
    """Show a printable ticket detail page for the logged-in attendee."""
    ticket = get_object_or_404(Ticket, pk=ticket_id, registration__user=request.user)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


@login_required
def organizer_ticket_sales(request, event_id):
    """Show per-event sales summary for organizers."""
    event = get_object_or_404(Event, pk=event_id)
    if event.organizer_id != request.user.id and not request.user.is_superuser:
        messages.error(request, 'You can only view sales for your own events.')
        return redirect('events:detail', event_id=event.id)

    tickets = Ticket.objects.filter(registration__event=event).select_related('registration__user')
    general_count = tickets.filter(ticket_type=Ticket.TicketType.GENERAL).count()
    vip_count = tickets.filter(ticket_type=Ticket.TicketType.VIP).count()
    premium_count = tickets.filter(ticket_type=Ticket.TicketType.PREMIUM).count()
    
    total_revenue = (
        general_count * event.ticket_price +
        vip_count * event.ticket_price_vip +
        premium_count * event.ticket_price_premium
    )
    
    summary = {
        'total_tickets': tickets.count(),
        'general': general_count,
        'vip': vip_count,
        'premium': premium_count,
        'revenue': total_revenue,
    }
    return render(request, 'tickets/organizer_sales.html', {'event': event, 'tickets': tickets, 'summary': summary})
