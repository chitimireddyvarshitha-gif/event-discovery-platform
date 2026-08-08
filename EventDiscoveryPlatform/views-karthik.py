from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count

from events.models import Event
from registrations.models import Registration
from accounts.models import User


def home(request):
    """Render the public landing page for the event platform with dynamic context."""
    now = timezone.now()
    
    # 1. Fetch top 3 upcoming events (annotated with registration counts)
    upcoming_events = Event.objects.filter(date__gte=now).select_related('organizer').annotate(
        reg_count=Count('registrations')
    ).order_by('date')[:3]
    
    # 2. Fetch platform stats
    total_events = Event.objects.filter(date__gte=now).count()
    total_registrations = Registration.objects.filter(status='confirmed').count()
    active_organizers = User.objects.filter(role='organizer').count()
    
    context = {
        'upcoming_events': upcoming_events,
        'total_events': total_events,
        'total_registrations': total_registrations,
        'active_organizers': active_organizers,
    }
    return render(request, "home.html", context)
