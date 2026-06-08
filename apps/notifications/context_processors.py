from .models import Notification


def notifications(request):
    if not request.user.is_authenticated:
        return {
            'unread_notification_count': 0,
            'latest_notifications': [],
        }

    user_notifications = Notification.objects.filter(user=request.user)
    return {
        'unread_notification_count': user_notifications.filter(
            is_read=False,
        ).count(),
        'latest_notifications': user_notifications[:5],
    }

