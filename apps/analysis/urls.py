from django.urls import path

from . import views

urlpatterns = [
    path('analyze/', views.analyze_form, name='analyze_form'),
    path(
        'analyze/result/<int:match_result_id>/',
        views.analysis_result,
        name='analysis_result',
    ),
]
