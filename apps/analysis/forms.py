from django import forms

from apps.jobs.models import JobDescription
from apps.resumes.models import Resume


class AnalyzeForm(forms.Form):
    resume = forms.ModelChoiceField(queryset=Resume.objects.none())
    job_description = forms.ModelChoiceField(queryset=JobDescription.objects.none())

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['resume'].queryset = Resume.objects.filter(user=user)
        self.fields['job_description'].queryset = JobDescription.objects.filter(user=user)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-select'})
