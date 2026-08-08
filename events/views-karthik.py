from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from favorites.models import Favorite
from registrations.models import Registration

from .forms import EventForm
from .models import Event


from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Event, EventCategory


def event_list(request):
    """Display all public events with search, filtering, sorting, and pagination."""
    # Annotate registrations count to support sorting by popularity
    events = Event.objects.select_related('organizer').annotate(
        reg_count=Count('registrations')
    )

    # 1. Search Query (name or description)
    q = request.GET.get('q', '').strip()
    if q:
        events = events.filter(
            Q(event_name__icontains=q) | 
            Q(description__icontains=q)
        )

    # 2. Category Filter
    category = request.GET.get('category', '').strip()
    if category:
        events = events.filter(category=category)

    # 3. Location Filter (venue city/location text search)
    location = request.GET.get('location', '').strip()
    if location:
        events = events.filter(venue__icontains=location)

    # 4. Price Filter (free vs paid)
    price_filter = request.GET.get('price', '').strip()
    if price_filter == 'free':
        events = events.filter(ticket_price=0)
    elif price_filter == 'paid':
        events = events.filter(ticket_price__gt=0)

    # 5. Date Filter (upcoming vs past vs all)
    now = timezone.now()
    date_filter = request.GET.get('date_filter', 'upcoming').strip()
    if date_filter == 'upcoming':
        events = events.filter(date__gte=now)
    elif date_filter == 'past':
        events = events.filter(date__lt=now)

    # 6. Sorting
    sort_by = request.GET.get('sort_by', 'date').strip()
    if sort_by == 'popular':
        events = events.order_by('-reg_count', '-date')
    else:
        events = events.order_by('date' if date_filter == 'upcoming' else '-date')

    # Get user's favorites and registrations if logged in for fast lookup on the list page
    favorite_event_ids = set()
    registered_event_ids = set()
    if request.user.is_authenticated:
        favorite_event_ids = set(
            Favorite.objects.filter(user=request.user).values_list('event_id', flat=True)
        )
        registered_event_ids = set(
            Registration.objects.filter(user=request.user, status='confirmed').values_list('event_id', flat=True)
        )

    # 7. Pagination (6 items per page)
    paginator = Paginator(events, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = EventCategory.choices

    context = {
        'page_obj': page_obj,
        'favorite_event_ids': favorite_event_ids,
        'registered_event_ids': registered_event_ids,
        'q': q,
        'selected_category': category,
        'location': location,
        'price': price_filter,
        'date_filter': date_filter,
        'sort_by': sort_by,
        'categories': categories,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        response = render(request, 'events/event_list_snippet.html', context)
        response['X-Has-Next'] = 'true' if page_obj.has_next() else 'false'
        return response
    return render(request, 'events/event_list.html', context)


def event_detail(request, event_id):
    """Show the details of a single event."""
    event = get_object_or_404(Event, pk=event_id)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, event=event).exists()
    return render(request, 'events/event_detail.html', {'event': event, 'is_favorite': is_favorite})


@login_required
def event_create(request):
    """Allow organizers to create a new event."""
    if request.user.role != 'organizer':
        messages.error(request, 'Only organizers can create events.')
        return redirect('events:list')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('events:detail', event_id=event.id)
    else:
        form = EventForm()

    return render(request, 'events/event_form.html', {'form': form})


@login_required
def event_edit(request, event_id):
    """Allow organizers to edit their own events."""
    event = get_object_or_404(Event, pk=event_id)
    if event.organizer_id != request.user.id:
        messages.error(request, 'You can only edit your own events.')
        return redirect('events:list')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            
            # Notify registered attendees of changes
            from django.urls import reverse
            from django.core.mail import send_mail
            from django.conf import settings
            from registrations.models import Registration
            from notifications.models import Notification
            from accounts.models import User

            attendees = User.objects.filter(
                id__in=Registration.objects.filter(event=event, status='confirmed').values_list('user_id', flat=True)
            )
            
            title = f"Event Updated: {event.event_name}"
            detail_url = request.build_absolute_uri(reverse('events:detail', kwargs={'event_id': event.id}))
            message = (
                f"The organizer has updated details for the event: {event.event_name}.\n\n"
                f"Please review the changes on the event details page.\n"
                f"Link: {detail_url}"
            )
            
            # Bulk create in-app notifications
            notifications = [
                Notification(user=attendee, title=title, message=message)
                for attendee in attendees
            ]
            Notification.objects.bulk_create(notifications)
            
            # Send emails
            for attendee in attendees:
                if attendee.email:
                    try:
                        send_mail(
                            subject=title,
                            message=message,
                            from_email=getattr(settings, 'EMAIL_FROM_USER', 'no-reply@eventhub.com'),
                            recipient_list=[attendee.email],
                            fail_silently=True
                        )
                    except Exception:
                        pass
            
            messages.success(request, 'Event updated successfully.')
            return redirect('events:detail', event_id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form})


@login_required
def event_delete(request, event_id):
    """Allow organizers to delete their own events."""
    event = get_object_or_404(Event, pk=event_id)
    if event.organizer_id != request.user.id:
        messages.error(request, 'You can only delete your own events.')
        return redirect('events:list')

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('events:list')

    return render(request, 'events/event_confirm_delete.html', {'event': event})


@login_required
def event_participants(request, event_id):
    """Show a list of registered attendees for an event to the organizer."""
    event = get_object_or_404(Event, pk=event_id)
    if event.organizer_id != request.user.id and not request.user.is_superuser:
        messages.error(request, 'You can only view participants for your own events.')
        return redirect('events:detail', event_id=event.id)

    registrations = Registration.objects.filter(event=event).select_related('user').order_by('-registration_date')
    return render(request, 'events/participants.html', {'event': event, 'registrations': registrations})
