from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnalyzeForm
from .models import JDMatchResult
from .services import analyze_resume_against_jd


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
