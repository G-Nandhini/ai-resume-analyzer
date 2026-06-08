from django.db import models

from apps.jobs.models import JobDescription
from apps.resumes.models import Resume


class ResumeAnalysis(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='analyses',
    )
    resume_score = models.FloatField(default=0)
    skills_found = models.JSONField(default=list)
    missing_sections = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)
    ai_insights = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'resume analyses'

    def __str__(self):
        return f'Analysis for {self.resume}'


class JDMatchResult(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='jd_match_results',
    )
    job_description = models.ForeignKey(
        JobDescription,
        on_delete=models.CASCADE,
        related_name='match_results',
    )
    resume_analysis = models.ForeignKey(
        ResumeAnalysis,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='jd_match_results',
    )
    match_score = models.FloatField(default=0)
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.resume} match for {self.job_description}'


class InterviewQuestion(models.Model):
    HR = 'HR'
    TECHNICAL = 'Technical'
    PROJECT_BASED = 'Project Based'

    QUESTION_TYPE_CHOICES = (
        (HR, 'HR'),
        (TECHNICAL, 'Technical'),
        (PROJECT_BASED, 'Project Based'),
    )

    match_result = models.ForeignKey(
        JDMatchResult,
        on_delete=models.CASCADE,
        related_name='interview_questions',
    )
    question_type = models.CharField(
        max_length=50,
        choices=QUESTION_TYPE_CHOICES,
    )
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question_type', 'created_at']

    def __str__(self):
        return f'{self.question_type} question for {self.match_result}'
