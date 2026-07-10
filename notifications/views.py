from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse

from .models import Notification


@login_required
def notification_list(request):
    """Inbox showing all notifications for the logged-in user."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})


@login_required
def mark_as_read(request, notification_id):
    """Mark a notification as read and return JSON for AJAX toggles."""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read.'
        })

    messages.success(request, 'Notification marked as read.')
    return redirect('notifications:list')


@login_required
def unread_count_api(request):
    """Return JSON count of unread notifications for the header bell."""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    recent_notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    recent_list = [
        {
            'id': n.id,
            'title': n.title,
            'created_at': n.created_at.strftime('%b %d, %H:%M')
        }
        for n in recent_notifications
    ]
    return JsonResponse({
        'unread_count': count,
        'recent_notifications': recent_list
    })
