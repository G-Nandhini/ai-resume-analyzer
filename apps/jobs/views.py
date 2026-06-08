from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.notifications.helpers import create_notification

from .forms import JobDescriptionForm
from .models import JobDescription


@login_required
def job_list(request):
    jobs = JobDescription.objects.filter(user=request.user)
    return render(request, 'jobs/job_list.html', {'jobs': jobs})


@login_required
def job_create(request):
    form = JobDescriptionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        job.user = request.user
        job.save()
        create_notification(
            request.user,
            'Job description created',
            f'{job.job_title} has been added to your job descriptions.',
        )
        messages.success(request, 'Job description saved successfully.')

        if request.POST.get('action') == 'analyze':
            return redirect('analyze_form')

        return redirect('job_list')

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'page_heading': 'Create Job Description',
    })


@login_required
def job_edit(request, id):
    job = get_object_or_404(JobDescription, id=id, user=request.user)
    form = JobDescriptionForm(request.POST or None, instance=job)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Job description updated successfully.')

        if request.POST.get('action') == 'analyze':
            return redirect('analyze_form')

        return redirect('job_list')

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'job': job,
        'page_heading': 'Edit Job Description',
    })


@login_required
def job_delete(request, id):
    job = get_object_or_404(JobDescription, id=id, user=request.user)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job description deleted successfully.')
        return redirect('job_list')

    return render(request, 'jobs/job_confirm_delete.html', {'job': job})
