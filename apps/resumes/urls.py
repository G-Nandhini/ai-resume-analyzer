from django.urls import path

from . import views

urlpatterns = [
    path('resumes/', views.resume_list, name='resume_list'),
    path('resumes/upload/', views.resume_upload, name='resume_upload'),
    path('resumes/<int:id>/', views.resume_detail, name='resume_detail'),
    path('resumes/<int:id>/delete/', views.resume_delete, name='resume_delete'),
]
