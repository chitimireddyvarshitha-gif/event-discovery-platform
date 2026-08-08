from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ProfileForm, RegistrationForm
from .models import User


def register_view(request):
    """Create a new attendee or organizer account."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'organizer':
                messages.warning(request, 'Your organizer account has been created successfully and is pending approval from a super admin. You will be able to log in once approved.')
                return redirect('accounts:login')
            else:
                login(request, user)
                messages.success(request, 'Your account has been created successfully.')
                return redirect('accounts:dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Log a user in and redirect by role."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role == 'organizer' and not user.is_approved:
                messages.warning(request, 'Your organizer account is pending approval from a super admin.')
                return render(request, 'accounts/login.html')
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('accounts:dashboard')
        messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Log the current user out."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    """Allow the current user to update profile details."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


from django.db.models import Sum, Count
from registrations.models import Registration
from favorites.models import Favorite
from tickets.models import Ticket
from events.models import Event


@login_required
def dashboard_view(request):
    """Render the user dashboard landing page with stats depending on the user role."""
    context = {'today': timezone.now()}
    if request.user.is_superuser:
        # Group events by organizer for the super admin
        organizers_with_events = User.objects.filter(role='organizer').prefetch_related('organized_events')
        grouped_data = []
        for org in organizers_with_events:
            org_events = org.organized_events.annotate(reg_count=Count('registrations')).order_by('-date')
            if org_events.exists():
                org_regs = Registration.objects.filter(event__organizer=org).count()
                org_revenue = 0
                tickets = Ticket.objects.filter(registration__event__organizer=org, registration__status='confirmed')
                for t in tickets:
                    evt = t.registration.event
                    if t.ticket_type == 'vip':
                        org_revenue += evt.ticket_price_vip
                    elif t.ticket_type == 'premium':
                        org_revenue += evt.ticket_price_premium
                    else:
                        org_revenue += evt.ticket_price
                grouped_data.append({
                    'organizer': org,
                    'events': org_events,
                    'total_events': org_events.count(),
                    'total_registrations': org_regs,
                    'total_revenue': org_revenue
                })
        context['grouped_organizers'] = grouped_data
        context['pending_organizers'] = User.objects.filter(role='organizer', is_approved=False)
        
        all_events = Event.objects.annotate(
            reg_count=Count('registrations')
        ).order_by('-date')
        context['events'] = all_events
        context['total_events'] = all_events.count()
        context['total_registrations'] = Registration.objects.count()
        
        tickets = Ticket.objects.filter(registration__status='confirmed')
        revenue = 0
        for t in tickets:
            evt = t.registration.event
            if t.ticket_type == 'vip':
                revenue += evt.ticket_price_vip
            elif t.ticket_type == 'premium':
                revenue += evt.ticket_price_premium
            else:
                revenue += evt.ticket_price
        context['total_revenue'] = revenue
        context['is_admin'] = True
    elif request.user.role == 'organizer':
        organized_events = Event.objects.filter(organizer=request.user).annotate(
            reg_count=Count('registrations')
        ).order_by('-date')
        context['events'] = organized_events
        context['total_events'] = organized_events.count()
        context['total_registrations'] = Registration.objects.filter(event__organizer=request.user).count()
        
        # Calculate revenue based on actual model pricing fields
        tickets = Ticket.objects.filter(registration__event__organizer=request.user, registration__status='confirmed')
        revenue = 0
        for t in tickets:
            evt = t.registration.event
            if t.ticket_type == 'vip':
                revenue += evt.ticket_price_vip
            elif t.ticket_type == 'premium':
                revenue += evt.ticket_price_premium
            else:
                revenue += evt.ticket_price
        context['total_revenue'] = revenue
        
        # Get pending attendee registrations for this organizer
        pending_bookings = Registration.objects.filter(
            event__organizer=request.user,
            status='pending'
        ).select_related('user', 'event').order_by('-registration_date')
        context['pending_bookings'] = pending_bookings
    else:
        # Attendee
        context['registrations'] = Registration.objects.filter(user=request.user).select_related('event', 'event__organizer').order_by('-registration_date')[:5]
        context['favorites'] = Favorite.objects.filter(user=request.user).select_related('event', 'event__organizer').order_by('-created_at')[:5]
        context['tickets_count'] = Ticket.objects.filter(registration__user=request.user).count()
        context['registrations_count'] = Registration.objects.filter(user=request.user).count()
        context['favorites_count'] = Favorite.objects.filter(user=request.user).count()

    return render(request, 'accounts/dashboard.html', context)


@login_required
def approve_organizer(request, user_id):
    """Allow super admins to approve pending organizers directly from the dashboard."""
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied.')
        return redirect('accounts:dashboard')
        
    organizer = get_object_or_404(User, pk=user_id, role='organizer')
    organizer.is_approved = True
    organizer.save()
    messages.success(request, f'Organizer account {organizer.username} has been approved successfully.')
    return redirect('accounts:dashboard')
