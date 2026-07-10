from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from events.models import Event

from .models import Favorite


@login_required
def favorite_list(request):
    """Show the authenticated user's saved events."""
    favorites = Favorite.objects.filter(user=request.user).select_related('event', 'event__organizer').order_by('-created_at')
    return render(request, 'favorites/favorite_list.html', {'favorites': favorites})


@login_required
def toggle_favorite(request, event_id):
    """Add or remove an event from the user's favorites, supporting both AJAX and redirects."""
    event = get_object_or_404(Event, pk=event_id)
    favorite, created = Favorite.objects.filter(user=request.user, event=event).first(), False
    
    if favorite:
        favorite.delete()
        is_favorite = False
        message = 'Removed from your favorites.'
    else:
        Favorite.objects.create(user=request.user, event=event)
        is_favorite = True
        message = 'Added to your favorites.'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })

    if is_favorite:
        messages.success(request, message)
    else:
        messages.info(request, message)

    return redirect('events:detail', event_id=event.id)
