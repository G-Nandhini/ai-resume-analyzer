from django.contrib import admin

from .models import JobDescription


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company_name', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('job_title', 'company_name', 'required_skills', 'description')
