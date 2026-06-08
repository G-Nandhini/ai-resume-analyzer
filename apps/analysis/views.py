from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max
from django.shortcuts import get_object_or_404, redirect, render

from apps.jobs.models import JobDescription
from apps.notifications.helpers import create_notification
from apps.resumes.models import Resume

from .forms import AnalyzeForm
from .ai_service import (
    AIServiceNotConfigured,
    AIServiceRequestError,
    generate_ai_resume_insights,
)
from .models import InterviewQuestion, JDMatchResult
from .services import analyze_resume_against_jd, generate_basic_interview_questions


def landing_page(request):
    return render(request, 'landing.html')


@login_required
def dashboard(request):
    user_match_results = JDMatchResult.objects.filter(
        resume__user=request.user,
        job_description__user=request.user,
    )
    score_summary = user_match_results.aggregate(
        average_match_score=Avg('match_score'),
        best_match_score=Max('match_score'),
    )
    recent_analyses = user_match_results.select_related(
        'resume',
        'job_description',
        'resume_analysis',
    )[:10]
    total_resumes = Resume.objects.filter(user=request.user).count()
    total_job_descriptions = JobDescription.objects.filter(
        user=request.user,
    ).count()
    total_analyses = user_match_results.count()
    user_display_name = (
        request.user.get_full_name()
        or request.user.first_name
        or request.user.username
    )

    context = {
        'user_display_name': user_display_name,
        'total_resumes': total_resumes,
        'total_job_descriptions': total_job_descriptions,
        'total_analyses': total_analyses,
        'average_match_score': score_summary['average_match_score'] or 0,
        'best_match_score': score_summary['best_match_score'] or 0,
        'has_resumes': total_resumes > 0,
        'has_job_descriptions': total_job_descriptions > 0,
        'has_analyses': total_analyses > 0,
        'recent_analyses': recent_analyses,
    }
    return render(request, 'dashboard.html', context)


@login_required
def analyze_form(request):
    form = AnalyzeForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        match_result = analyze_resume_against_jd(
            form.cleaned_data['resume'],
            form.cleaned_data['job_description'],
        )
        create_notification(
            request.user,
            'Resume analysis completed',
            (
                f'{match_result.resume.title} was analyzed for '
                f'{match_result.job_description.job_title}.'
            ),
        )
        messages.success(request, 'Resume analysis completed successfully.')
        return redirect('analysis_result', match_result_id=match_result.id)

    return render(request, 'analysis/analyze_form.html', {'form': form})


@login_required
def analysis_result(request, match_result_id):
    match_result = get_object_or_404(
        JDMatchResult.objects.select_related(
            'resume',
            'job_description',
            'resume_analysis',
        ),
        id=match_result_id,
        resume__user=request.user,
        job_description__user=request.user,
    )

    return render(request, 'analysis/analysis_result.html', {'match_result': match_result})


@login_required
def generate_ai_insights(request, match_result_id):
    match_result = get_object_or_404(
        JDMatchResult.objects.select_related(
            'resume',
            'job_description',
            'resume_analysis',
        ),
        id=match_result_id,
        resume__user=request.user,
        job_description__user=request.user,
    )

    if request.method != 'POST':
        return redirect('analysis_result', match_result_id=match_result.id)

    if not match_result.resume_analysis:
        messages.warning(request, 'Resume analysis details are not available.')
        return redirect('analysis_result', match_result_id=match_result.id)

    try:
        job_description = match_result.job_description
        job_description_text = '\n'.join([
            line
            for label, value in (
                ('Job Title', job_description.job_title),
                ('Company', job_description.company_name),
                ('Experience Required', job_description.experience_required),
                ('Required Skills', job_description.required_skills),
                ('Description', job_description.description),
            )
            if value
            for line in (f'{label}: {value}',)
        ])
        ai_insights = generate_ai_resume_insights(
            match_result.resume.extracted_text,
            job_description_text,
        )
    except AIServiceNotConfigured:
        messages.warning(request, 'AI is not configured yet.')
    except AIServiceRequestError as exc:
        messages.error(request, exc.message)
    except Exception:
        messages.error(request, 'AI insights could not be generated right now.')
    else:
        match_result.resume_analysis.ai_insights = ai_insights
        match_result.resume_analysis.save(update_fields=['ai_insights'])
        create_notification(
            request.user,
            'AI insights generated',
            f'AI insights are ready for {match_result.resume.title}.',
        )
        messages.success(request, 'AI insights generated successfully.')

    return redirect('analysis_result', match_result_id=match_result.id)


@login_required
def latest_interview_questions(request):
    match_result = JDMatchResult.objects.filter(
        resume__user=request.user,
        job_description__user=request.user,
    ).first()

    if not match_result:
        messages.info(
            request,
            'Analyze a resume against a job description to generate interview questions.',
        )
        return redirect('analyze_form')

    return redirect('interview_questions', match_result_id=match_result.id)


@login_required
def interview_questions(request, match_result_id):
    match_result = get_object_or_404(
        JDMatchResult.objects.select_related(
            'resume',
            'job_description',
        ),
        id=match_result_id,
        resume__user=request.user,
        job_description__user=request.user,
    )
    questions = generate_basic_interview_questions(match_result)

    context = {
        'match_result': match_result,
        'hr_questions': questions.filter(question_type=InterviewQuestion.HR),
        'technical_questions': questions.filter(
            question_type=InterviewQuestion.TECHNICAL,
        ),
        'project_based_questions': questions.filter(
            question_type=InterviewQuestion.PROJECT_BASED,
        ),
    }
    return render(request, 'analysis/interview_questions.html', context)
