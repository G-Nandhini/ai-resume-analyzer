from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.text import slugify
from weasyprint import HTML

from apps.analysis.models import JDMatchResult
from apps.notifications.helpers import create_notification


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


@login_required
def report_download(request, match_result_id):
    match_result = get_object_or_404(
        JDMatchResult.objects.select_related(
            'resume',
            'job_description',
            'resume_analysis',
        ).prefetch_related('interview_questions'),
        id=match_result_id,
        resume__user=request.user,
        job_description__user=request.user,
    )
    html = render_to_string(
        'reports/report_pdf.html',
        {
            'match_result': match_result,
            'interview_questions': match_result.interview_questions.all(),
        },
        request=request,
    )
    pdf = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
    filename = slugify(
        f'{match_result.resume.title}-{match_result.job_description.job_title}-report',
    )

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    create_notification(
        request.user,
        'PDF report downloaded',
        f'The report for {match_result.resume.title} was downloaded.',
    )
    return response
