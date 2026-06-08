from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.analysis.models import JDMatchResult


@login_required
def report_list(request):
    match_results = JDMatchResult.objects.filter(
        resume__user=request.user,
        job_description__user=request.user,
    ).select_related(
        'resume',
        'job_description',
        'resume_analysis',
    )

    return render(
        request,
        'reports/report_list.html',
        {'match_results': match_results},
    )


@login_required
def report_detail(request, match_result_id):
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

    return render(
        request,
        'reports/report_detail.html',
        {'match_result': match_result},
    )
