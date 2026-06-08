from django.contrib.auth.models import User
from django.db import models


class JobDescription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_descriptions',
    )
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    experience_required = models.CharField(max_length=255, blank=True, null=True)
    required_skills = models.TextField(blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.company_name:
            return f'{self.job_title} at {self.company_name}'
        return self.job_title
