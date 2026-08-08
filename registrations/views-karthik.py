from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from events.models import Event
from .models import Registration


@login_required
def my_registrations(request):
    """Show the logged-in attendee's registration history."""
    registrations = Registration.objects.filter(user=request.user).select_related('event').order_by('-registration_date')
    return render(request, 'registrations/my_registrations.html', {'registrations': registrations})


@login_required
def register_for_event(request, event_id):
    """Register the current user for a specific event, with ticket choice and confirmation."""
    event = get_object_or_404(Event, pk=event_id)
    
    # Restrict organizers from registering
    if request.user.role == 'organizer' or request.user.is_superuser:
        messages.error(request, 'Organizers and administrators cannot register for events.')
        return redirect('events:detail', event_id=event.id)

    if request.method == 'POST':
        ticket_type = request.POST.get('ticket_type', 'general')
        card_number = request.POST.get('card_number', '').strip()
        card_name = request.POST.get('card_name', '').strip()
        
        # Calculate selected ticket price
        price = event.ticket_price
        if ticket_type == 'vip':
            price = event.ticket_price_vip
        elif ticket_type == 'premium':
            price = event.ticket_price_premium
            
        # Check capacity
        if event.registrations.filter(status='confirmed').count() >= event.capacity:
            messages.error(request, 'This event is fully booked.')
            return redirect('events:detail', event_id=event.id)
            
        try:
            status = 'pending' if price > 0 else 'confirmed'
            payment_details = ""
            if price > 0:
                payment_details = f"Cardholder: {card_name} | Card: **** **** **** {card_number[-4:] if len(card_number) >= 4 else '1111'}"
            else:
                payment_details = "Free Event (No Payment Required)"
                
            reg = Registration.objects.create(
                user=request.user,
                event=event,
                status=status,
                ticket_type=ticket_type,
                payment_details=payment_details
            )
            
            if status == 'confirmed':
                messages.success(request, f'Registration confirmed for {event.event_name}! Your ticket has been issued.')
            else:
                messages.warning(request, f'Your booking request for {event.event_name} is pending organizer payment verification.')
            return redirect('registrations:my_registrations')
            
        except IntegrityError:
            messages.info(request, 'You are already registered for this event.')
            return redirect('registrations:my_registrations')

    # GET request - render confirmation screen
    prices = {
        'general': event.ticket_price,
        'vip': event.ticket_price_vip,
        'premium': event.ticket_price_premium,
    }
    
    return render(request, 'registrations/confirm_registration.html', {
        'event': event,
        'prices': prices
    })


@login_required
def approve_registration(request, registration_id):
    """Allow organizers to approve a pending registration."""
    registration = get_object_or_404(Registration, pk=registration_id)
    
    # Verify request.user is the organizer of the event (or super admin)
    if not request.user.is_superuser and registration.event.organizer != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('accounts:dashboard')
        
    registration.status = 'confirmed'
    registration.save()  # Triggers post-save signal which issues the ticket!
    messages.success(request, f'Registration for {registration.user.username} has been approved and ticket issued.')
    return redirect('accounts:dashboard')


@login_required
def reject_registration(request, registration_id):
    """Allow organizers to cancel/reject a pending registration."""
    registration = get_object_or_404(Registration, pk=registration_id)
    
    # Verify request.user is the organizer of the event (or super admin)
    if not request.user.is_superuser and registration.event.organizer != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('accounts:dashboard')
        
    registration.status = 'cancelled'
    registration.save()
    messages.warning(request, f'Registration for {registration.user.username} has been rejected/cancelled.')
    return redirect('accounts:dashboard')
