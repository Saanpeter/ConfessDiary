from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).select_related('actor', 'target_content_type')
    notifications.filter(read=False).update(read=True)
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})


@login_required
def mark_notification_read(request, notification_id):
    notification = Notification.objects.filter(recipient=request.user, id=notification_id).first()
    if notification is not None:
        notification.read = True
        notification.save(update_fields=['read'])
        messages.success(request, 'Notification marked as read.')
    return redirect('notification_list')
