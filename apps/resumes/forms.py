from pathlib import Path

from django import forms

from .models import Resume


class ResumeForm(forms.ModelForm):
    max_file_size = 5 * 1024 * 1024
    allowed_extensions = {'.pdf', '.docx'}

    class Meta:
        model = Resume
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Nandhini Resume',
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx',
            }),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if not uploaded_file:
            return uploaded_file

        extension = Path(uploaded_file.name).suffix.lower()
        if extension not in self.allowed_extensions:
            raise forms.ValidationError('Only PDF and DOCX files are allowed.')

        if uploaded_file.size > self.max_file_size:
            raise forms.ValidationError('Resume file size must be 5MB or less.')

        return uploaded_file
