from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import JobDescriptionForm
from .models import JobDescription


class JobDescriptionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jobuser',
            password='S3cure-Passphrase-2026',
        )

    def test_string_representation_includes_company_when_present(self):
        job = JobDescription.objects.create(
            user=self.user,
            job_title='Backend Developer',
            company_name='Acme',
            description='Build APIs.',
        )

        self.assertEqual(str(job), 'Backend Developer at Acme')

    def test_default_ordering_shows_newest_first(self):
        older = JobDescription.objects.create(
            user=self.user,
            job_title='Older Role',
            description='Older description.',
        )
        newer = JobDescription.objects.create(
            user=self.user,
            job_title='Newer Role',
            description='Newer description.',
        )
        JobDescription.objects.filter(pk=older.pk).update(
            created_at=timezone.now() - timedelta(days=1),
        )
        JobDescription.objects.filter(pk=newer.pk).update(created_at=timezone.now())

        self.assertEqual(
            list(JobDescription.objects.values_list('job_title', flat=True)),
            ['Newer Role', 'Older Role'],
        )


class JobDescriptionFormTests(TestCase):
    def test_valid_form_accepts_required_fields_only(self):
        form = JobDescriptionForm(data={
            'job_title': 'Python Developer',
            'description': 'Build and maintain Django applications.',
        })

        self.assertTrue(form.is_valid(), form.errors)

    def test_job_title_and_description_are_required(self):
        form = JobDescriptionForm(data={
            'job_title': '',
            'description': '',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('job_title', form.errors)
        self.assertIn('description', form.errors)

    def test_fields_include_bootstrap_class(self):
        form = JobDescriptionForm()

        self.assertEqual(form.fields['job_title'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['description'].widget.attrs['class'], 'form-control')


class JobDescriptionViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            password='S3cure-Passphrase-2026',
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='S3cure-Passphrase-2026',
        )
        self.job = JobDescription.objects.create(
            user=self.user,
            job_title='Owner Role',
            company_name='Owner Co',
            description='Owner description.',
        )

    def test_job_list_requires_login(self):
        response = self.client.get(reverse('job_list'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('job_list')}",
        )

    def test_job_list_only_shows_current_users_jobs(self):
        other_job = JobDescription.objects.create(
            user=self.other_user,
            job_title='Other Role',
            description='Other description.',
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('job_list'))

        self.assertContains(response, self.job.job_title)
        self.assertNotContains(response, other_job.job_title)

    def test_create_saves_job_for_logged_in_user(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('job_create'), {
            'job_title': 'Data Engineer',
            'company_name': 'Data Co',
            'experience_required': '4 years',
            'required_skills': 'Python, SQL',
            'description': 'Build data pipelines.',
            'action': 'save',
        })

        job = JobDescription.objects.get(job_title='Data Engineer')
        self.assertEqual(job.user, self.user)
        self.assertRedirects(response, reverse('job_list'))

    def test_save_and_analyze_saves_job_and_returns_to_list(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('job_create'), {
            'job_title': 'ML Engineer',
            'description': 'Train production models.',
            'action': 'analyze',
        }, follow=True)

        self.assertTrue(JobDescription.objects.filter(job_title='ML Engineer').exists())
        self.assertContains(response, 'Analysis workflow will be available soon.')

    def test_edit_updates_only_owned_job(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('job_edit', kwargs={'id': self.job.id}), {
            'job_title': 'Updated Owner Role',
            'company_name': 'Owner Co',
            'experience_required': '5 years',
            'required_skills': 'Django',
            'description': 'Updated description.',
            'action': 'save',
        })

        self.job.refresh_from_db()
        self.assertEqual(self.job.job_title, 'Updated Owner Role')
        self.assertRedirects(response, reverse('job_list'))

    def test_edit_does_not_allow_access_to_another_users_job(self):
        self.client.force_login(self.other_user)

        response = self.client.get(reverse('job_edit', kwargs={'id': self.job.id}))

        self.assertEqual(response.status_code, 404)

    def test_delete_requires_post_and_removes_owned_job(self):
        self.client.force_login(self.user)

        get_response = self.client.get(reverse('job_delete', kwargs={'id': self.job.id}))
        post_response = self.client.post(reverse('job_delete', kwargs={'id': self.job.id}))

        self.assertEqual(get_response.status_code, 200)
        self.assertRedirects(post_response, reverse('job_list'))
        self.assertFalse(JobDescription.objects.filter(pk=self.job.pk).exists())

    def test_delete_does_not_allow_access_to_another_users_job(self):
        self.client.force_login(self.other_user)

        response = self.client.post(reverse('job_delete', kwargs={'id': self.job.id}))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(JobDescription.objects.filter(pk=self.job.pk).exists())
