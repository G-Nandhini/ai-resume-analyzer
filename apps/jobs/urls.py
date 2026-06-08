from django.urls import path

from . import views

urlpatterns = [
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:id>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:id>/delete/', views.job_delete, name='job_delete'),
]
