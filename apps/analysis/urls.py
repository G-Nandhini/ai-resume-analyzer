from django.urls import path

from . import views

urlpatterns = [
    path('analyze/', views.analyze_form, name='analyze_form'),
    path(
        'analysis/interview-questions/',
        views.latest_interview_questions,
        name='latest_interview_questions',
    ),
    path(
        'analyze/result/<int:match_result_id>/',
        views.analysis_result,
        name='analysis_result',
    ),
    path(
        'analyze/result/<int:match_result_id>/ai-insights/',
        views.generate_ai_insights,
        name='generate_ai_insights',
    ),
    path(
        'analysis/<int:match_result_id>/interview-questions/',
        views.interview_questions,
        name='interview_questions',
    ),
]
