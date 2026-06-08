from django.urls import path

from . import views

urlpatterns = [
    path('reports/', views.report_list, name='report_list'),
    path(
        'reports/<int:match_result_id>/',
        views.report_detail,
        name='report_detail',
    ),
]
