from django.contrib import admin

from .models import JDMatchResult, ResumeAnalysis


@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('resume', 'resume_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('resume__title', 'resume__user__username', 'resume__user__email')


@admin.register(JDMatchResult)
class JDMatchResultAdmin(admin.ModelAdmin):
    list_display = ('resume', 'job_description', 'match_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'resume__title',
        'job_description__job_title',
        'job_description__company_name',
    )
