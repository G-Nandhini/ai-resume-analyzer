from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max
from django.shortcuts import get_object_or_404, redirect, render

from apps.jobs.models import JobDescription
from apps.resumes.models import Resume

from .forms import AnalyzeForm
from .models import JDMatchResult
from .services import analyze_resume_against_jd


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

    context = {
        'total_resumes': Resume.objects.filter(user=request.user).count(),
        'total_job_descriptions': JobDescription.objects.filter(
            user=request.user,
        ).count(),
        'average_match_score': score_summary['average_match_score'] or 0,
        'best_match_score': score_summary['best_match_score'] or 0,
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
