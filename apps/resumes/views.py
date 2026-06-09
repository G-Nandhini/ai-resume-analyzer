from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import escape
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from apps.notifications.helpers import create_notification

from .forms import ResumeForm
from .models import Resume
from .services import ResumeTextExtractionError, extract_resume_text


def csrf_failure(request, reason=''):
    post_keys = ', '.join(escape(key) for key in request.POST.keys()) or 'none'
    cookie_status = 'present' if request.COOKIES.get('csrftoken') else 'missing'
    content_type = escape(request.META.get('CONTENT_TYPE', 'unknown'))

    return HttpResponseForbidden(
        '<h1>Forbidden (403)</h1>'
        '<p>CSRF verification failed. Request aborted.</p>'
        '<h2>Debug details</h2>'
        f'<p><strong>Reason:</strong> {escape(reason)}</p>'
        f'<p><strong>CSRF cookie:</strong> {cookie_status}</p>'
        f'<p><strong>POST fields received:</strong> {post_keys}</p>'
        f'<p><strong>Content type:</strong> {content_type}</p>'
        '<p>Open /resumes/upload/ with a fresh GET request, then submit the form again.</p>',
    )


@login_required
def resume_list(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'resumes/resume_list.html', {'resumes': resumes})


@login_required
@never_cache
@csrf_protect
@ensure_csrf_cookie
def resume_upload(request):
    form = ResumeForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        resume = form.save(commit=False)
        resume.user = request.user
        resume.save()
        create_notification(
            request.user,
            'Resume uploaded',
            f'{resume.title} has been uploaded successfully.',
        )

        try:
            resume.extracted_text = extract_resume_text(resume)
            resume.save(update_fields=['extracted_text'])
            messages.success(request, 'Resume uploaded and text extracted successfully.')
        except ResumeTextExtractionError as exc:
            messages.warning(request, str(exc))

        return redirect('resume_detail', id=resume.id)
    if request.method == 'POST':
        print('Invalid resume upload POST keys:', list(request.POST.keys()), 'FILES:', list(request.FILES.keys()))
        messages.error(request, 'Please enter a resume title and choose a PDF or DOCX file.')

    return render(request, 'resumes/resume_upload.html', {'form': form})


@login_required
def resume_detail(request, id):
    resume = get_object_or_404(Resume, id=id, user=request.user)
    return render(request, 'resumes/resume_detail.html', {'resume': resume})


@login_required
def resume_delete(request, id):
    resume = get_object_or_404(Resume, id=id, user=request.user)
    if request.method == 'POST':
        resume.delete()
        messages.success(request, 'Resume deleted successfully.')
        return redirect('resume_list')

    return render(request, 'resumes/resume_detail.html', {
        'resume': resume,
        'confirm_delete': True,
    })
