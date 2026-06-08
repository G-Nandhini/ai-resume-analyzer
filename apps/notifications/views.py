from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(
        request,
        'notifications/list.html',
        {'notifications': notifications},
    )


@login_required
def mark_as_read(request, id):
    notification = get_object_or_404(
        Notification,
        id=id,
        user=request.user,
    )
    notification.is_read = True
    notification.save(update_fields=['is_read'])

    next_url = request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
    ):
        return redirect(next_url)
    return redirect('notifications')


@login_required
def mark_all_as_read(request):
    Notification.objects.filter(
        user=request.user,
        is_read=False,
    ).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')

    next_url = request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
    ):
        return redirect(next_url)
    return redirect('notifications')
