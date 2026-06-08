from collections import Counter
from itertools import chain

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import redirect, render

from apps.analysis.models import JDMatchResult
from apps.jobs.models import JobDescription
from apps.notifications.models import Notification
from apps.resumes.models import Resume

from .forms import LoginForm, RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    resumes = Resume.objects.filter(user=user)
    job_descriptions = JobDescription.objects.filter(user=user)
    match_results = JDMatchResult.objects.filter(
        resume__user=user,
        job_description__user=user,
    ).select_related('resume', 'job_description', 'resume_analysis')

    total_resumes = resumes.count()
    total_job_descriptions = job_descriptions.count()
    total_analyses = match_results.count()
    average_match_score = match_results.aggregate(
        average=Avg('match_score'),
    )['average'] or 0

    completion_items = [
        bool(user.username),
        bool(user.first_name),
        bool(user.last_name),
        bool(user.email),
        total_resumes > 0,
        total_job_descriptions > 0,
        total_analyses > 0,
    ]
    profile_completion = round(
        (sum(completion_items) / len(completion_items)) * 100,
    )

    matched_skill_counter = Counter()
    missing_skill_counter = Counter()
    learning_area_counter = Counter()

    for result in match_results[:20]:
        matched_skill_counter.update(result.matched_skills or [])
        missing_skill_counter.update(result.missing_skills or [])
        if result.resume_analysis:
            matched_skill_counter.update(result.resume_analysis.skills_found or [])
            learning_area_counter.update(result.resume_analysis.missing_sections or [])
            for suggestion in result.resume_analysis.suggestions or []:
                learning_area_counter.update([suggestion])

    recent_notifications = [
        {
            'icon': 'bi-bell',
            'title': notification.title,
            'description': notification.message,
            'created_at': notification.created_at,
        }
        for notification in Notification.objects.filter(user=user)[:5]
    ]
    recent_resume_activities = [
        {
            'icon': 'bi-file-earmark-arrow-up',
            'title': 'Resume uploaded',
            'description': resume.title,
            'created_at': resume.uploaded_at,
        }
        for resume in resumes[:5]
    ]
    recent_job_activities = [
        {
            'icon': 'bi-briefcase',
            'title': 'Job description added',
            'description': job.job_title,
            'created_at': job.created_at,
        }
        for job in job_descriptions[:5]
    ]
    recent_analysis_activities = [
        {
            'icon': 'bi-stars',
            'title': 'Resume analysis completed',
            'description': (
                f'{match.resume.title} matched with '
                f'{match.job_description.job_title}'
            ),
            'created_at': match.created_at,
        }
        for match in match_results[:5]
    ]
    recent_activities = sorted(
        chain(
            recent_notifications,
            recent_resume_activities,
            recent_job_activities,
            recent_analysis_activities,
        ),
        key=lambda activity: activity['created_at'],
        reverse=True,
    )[:5]

    context = {
        'display_name': user.get_full_name() or user.username,
        'avatar_initial': (
            user.first_name[:1] or user.username[:1] or 'U'
        ).upper(),
        'member_since': user.date_joined,
        'profile_completion': profile_completion,
        'total_resumes': total_resumes,
        'total_job_descriptions': total_job_descriptions,
        'total_analyses': total_analyses,
        'average_match_score': average_match_score,
        'recent_activities': recent_activities,
        'top_skills': matched_skill_counter.most_common(8),
        'missing_skills': missing_skill_counter.most_common(8),
        'suggested_learning_areas': learning_area_counter.most_common(5),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def dashboard_preview(request):
    return render(request, 'dashboard.html')
