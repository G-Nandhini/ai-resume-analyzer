from django.urls import path

from . import views

urlpatterns = [
    path('notifications/', views.notification_list, name='notifications'),
    path(
        'notifications/read/<int:id>/',
        views.mark_as_read,
        name='notification_read',
    ),
    path(
        'notifications/read-all/',
        views.mark_all_as_read,
        name='notifications_read_all',
    ),
]

