from django.urls import path

from . import views

urlpatterns = [
    path('analyze/', views.analyze_form, name='analyze_form'),
    path(
        'interview-questions/',
        views.interview_question_list,
        name='interview_question_list',
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
        'interview-questions/<int:match_result_id>/',
        views.interview_questions,
        name='interview_questions',
    ),
    path(
        'interview-questions/<int:match_result_id>/generate/',
        views.generate_interview_questions,
        name='generate_interview_questions',
    ),
]
