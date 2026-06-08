from django import forms

from .models import JobDescription


class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = [
            'job_title',
            'company_name',
            'experience_required',
            'required_skills',
            'description',
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Senior Python Developer',
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Acme Technologies',
            }),
            'experience_required': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 3-5 years',
            }),
            'required_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Python, Django, PostgreSQL, REST APIs',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Paste the full job description here.',
            }),
        }
