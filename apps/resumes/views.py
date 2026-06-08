from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ResumeForm
from .models import Resume
from .services import ResumeTextExtractionError, extract_resume_text


@login_required
def resume_list(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'resumes/resume_list.html', {'resumes': resumes})


@login_required
def resume_upload(request):
    form = ResumeForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        resume = form.save(commit=False)
        resume.user = request.user
        resume.save()

        try:
            resume.extracted_text = extract_resume_text(resume)
            resume.save(update_fields=['extracted_text'])
            messages.success(request, 'Resume uploaded and text extracted successfully.')
        except ResumeTextExtractionError as exc:
            messages.warning(request, str(exc))

        return redirect('resume_detail', id=resume.id)

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
