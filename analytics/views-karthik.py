import datetime
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from accounts.models import User
from events.models import Event, EventCategory
from registrations.models import Registration
from tickets.models import Ticket


@login_required
def reports_dashboard(request):
    """Serve the reports view with role-specific aggregated statistics."""
    role = request.user.role
    if request.user.is_superuser:
        role = 'admin'
    context = {'role': role}

    if role == 'organizer':
        # Organizer Stats
        hosted_events = Event.objects.filter(organizer=request.user)
        total_events = hosted_events.count()
        
        tickets = Ticket.objects.filter(registration__event__in=hosted_events)
        total_tickets = tickets.count()
        
        # Calculate revenue using actual database ticket prices
        total_revenue = Decimal('0.00')
        for ticket in tickets:
            evt = ticket.registration.event
            if ticket.ticket_type == Ticket.TicketType.VIP:
                total_revenue += evt.ticket_price_vip
            elif ticket.ticket_type == Ticket.TicketType.PREMIUM:
                total_revenue += evt.ticket_price_premium
            else:
                total_revenue += evt.ticket_price

        context.update({
            'total_events': total_events,
            'total_registrations': total_tickets,
            'total_revenue': total_revenue,
        })

    elif role == 'attendee':
        # Attendee Stats
        regs = Registration.objects.filter(user=request.user, status='confirmed')
        total_regs = regs.count()
        
        tickets = Ticket.objects.filter(registration__user=request.user)
        total_tickets = tickets.count()
        
        # Calculate money spent using actual database ticket prices
        total_spent = Decimal('0.00')
        for ticket in tickets:
            evt = ticket.registration.event
            if ticket.ticket_type == Ticket.TicketType.VIP:
                total_spent += evt.ticket_price_vip
            elif ticket.ticket_type == Ticket.TicketType.PREMIUM:
                total_spent += evt.ticket_price_premium
            else:
                total_spent += evt.ticket_price

        context.update({
            'total_registrations': total_regs,
            'total_tickets': total_tickets,
            'total_spent': total_spent,
        })

    else:
        # Admin / Superuser Stats
        context['role'] = 'admin'  # Treat admins and superusers uniformly here
        total_users = User.objects.count()
        total_attendees = User.objects.filter(role='attendee').count()
        total_organizers = User.objects.filter(role='organizer').count()
        total_events = Event.objects.count()
        total_bookings = Registration.objects.filter(status='confirmed').count()
        
        # Calculate total platform revenue using actual database ticket prices
        tickets = Ticket.objects.all()
        total_revenue = Decimal('0.00')
        for ticket in tickets:
            evt = ticket.registration.event
            if ticket.ticket_type == Ticket.TicketType.VIP:
                total_revenue += evt.ticket_price_vip
            elif ticket.ticket_type == Ticket.TicketType.PREMIUM:
                total_revenue += evt.ticket_price_premium
            else:
                total_revenue += evt.ticket_price

        context.update({
            'total_users': total_users,
            'total_attendees': total_attendees,
            'total_organizers': total_organizers,
            'total_events': total_events,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
        })

    return render(request, 'analytics/reports.html', context)


@login_required
def chart_data_api(request):
    """JSON API endpoint returning Chart.js datasets custom tailored to user role."""
    role = request.user.role
    if request.user.is_superuser:
        role = 'admin'
    data = {}

    if role == 'organizer':
        # 1. Registrations per Event (Top 5 events)
        events = Event.objects.filter(organizer=request.user).annotate(
            reg_count=Count('registrations')
        ).order_by('-created_at')[:5]
        
        event_names = [e.event_name for e in events]
        reg_counts = [e.reg_count for e in events]
        
        # 2. Ticket Types sold
        tickets = Ticket.objects.filter(registration__event__organizer=request.user)
        gen = tickets.filter(ticket_type=Ticket.TicketType.GENERAL).count()
        prem = tickets.filter(ticket_type=Ticket.TicketType.PREMIUM).count()
        vip = tickets.filter(ticket_type=Ticket.TicketType.VIP).count()

        data = {
            'bar': {
                'labels': event_names,
                'datasets': [{
                    'label': 'Registrations per Event',
                    'data': reg_counts,
                    'backgroundColor': 'rgba(99, 102, 241, 0.65)',
                    'borderColor': 'rgb(99, 102, 241)',
                    'borderWidth': 1
                }]
            },
            'doughnut': {
                'labels': ['General', 'Premium', 'VIP'],
                'datasets': [{
                    'label': 'Ticket Types Sold',
                    'data': [gen, prem, vip],
                    'backgroundColor': [
                        'rgba(148, 163, 184, 0.7)',
                        'rgba(14, 165, 233, 0.7)',
                        'rgba(245, 158, 11, 0.7)'
                    ]
                }]
            }
        }

    elif role == 'attendee':
        # 1. Spent per Category
        tickets = Ticket.objects.filter(registration__user=request.user).select_related('registration__event')
        cat_spent = {c.value: Decimal('0.00') for c in EventCategory}
        
        for ticket in tickets:
            event = ticket.registration.event
            val = Decimal('0.00')
            if ticket.ticket_type == Ticket.TicketType.VIP:
                val = event.ticket_price_vip
            elif ticket.ticket_type == Ticket.TicketType.PREMIUM:
                val = event.ticket_price_premium
            else:
                val = event.ticket_price
            cat_spent[event.category] += val
            
        categories = [c.label for c in EventCategory]
        spent_values = [float(cat_spent[c.value]) for c in EventCategory]

        # 2. Bookings over last 6 months
        now = timezone.now()
        months_labels = []
        bookings_counts = []
        
        for i in range(5, -1, -1):
            target_date = now - datetime.timedelta(days=i * 30)
            month_start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (month_start + datetime.timedelta(days=32)).replace(day=1)
            
            count = Registration.objects.filter(
                user=request.user,
                registration_date__gte=month_start,
                registration_date__lt=next_month,
                status='confirmed'
            ).count()
            
            months_labels.append(month_start.strftime('%b'))
            bookings_counts.append(count)

        data = {
            'doughnut': {
                'labels': categories,
                'datasets': [{
                    'label': 'Spent per Category ($)',
                    'data': spent_values,
                    'backgroundColor': [
                        'rgba(99, 102, 241, 0.7)',
                        'rgba(236, 72, 153, 0.7)',
                        'rgba(59, 130, 246, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(245, 158, 11, 0.7)',
                        'rgba(239, 68, 68, 0.7)'
                    ]
                }]
            },
            'line': {
                'labels': months_labels,
                'datasets': [{
                    'label': 'Confirmed Bookings',
                    'data': bookings_counts,
                    'borderColor': 'rgb(236, 72, 153)',
                    'backgroundColor': 'rgba(236, 72, 153, 0.15)',
                    'fill': True,
                    'tension': 0.3
                }]
            }
        }

    else:
        # Admin / Superuser
        # 1. User Signups over last 6 months
        now = timezone.now()
        months_labels = []
        signups_counts = []
        
        for i in range(5, -1, -1):
            target_date = now - datetime.timedelta(days=i * 30)
            month_start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (month_start + datetime.timedelta(days=32)).replace(day=1)
            
            count = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lt=next_month
            ).count()
            
            months_labels.append(month_start.strftime('%b'))
            signups_counts.append(count)

        # 2. Top Popular Events
        popular_events = Event.objects.annotate(
            reg_count=Count('registrations')
        ).order_by('-reg_count')[:5]
        
        event_names = [e.event_name for e in popular_events]
        event_counts = [e.reg_count for e in popular_events]

        data = {
            'line': {
                'labels': months_labels,
                'datasets': [{
                    'label': 'New User Registrations',
                    'data': signups_counts,
                    'borderColor': 'rgb(99, 102, 241)',
                    'backgroundColor': 'rgba(99, 102, 241, 0.15)',
                    'fill': True,
                    'tension': 0.3
                }]
            },
            'bar': {
                'labels': event_names,
                'datasets': [{
                    'label': 'Popular Events (Registrations)',
                    'data': event_counts,
                    'backgroundColor': 'rgba(236, 72, 153, 0.65)',
                    'borderColor': 'rgb(236, 72, 153)',
                    'borderWidth': 1
                }]
            }
        }

    return JsonResponse(data)
