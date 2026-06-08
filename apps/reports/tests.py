from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.analysis.models import InterviewQuestion, JDMatchResult, ResumeAnalysis
from apps.jobs.models import JobDescription
from apps.resumes.models import Resume


class ReportViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='report-owner',
            password='S3cure-Passphrase-2026',
        )
        self.other_user = User.objects.create_user(
            username='report-other',
            password='S3cure-Passphrase-2026',
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title='Owner Resume',
            file='resumes/owner.pdf',
            extracted_text='Skills: Python, Django',
        )
        self.other_resume = Resume.objects.create(
            user=self.other_user,
            title='Other Resume',
            file='resumes/other.pdf',
            extracted_text='Skills: Java',
        )
        self.job_description = JobDescription.objects.create(
            user=self.user,
            job_title='Backend Developer',
            company_name='Acme',
            required_skills='Python, Django',
            description='Build backend services.',
        )
        self.other_job_description = JobDescription.objects.create(
            user=self.other_user,
            job_title='Other Developer',
            required_skills='Java',
            description='Build Java services.',
        )
        self.resume_analysis = ResumeAnalysis.objects.create(
            resume=self.resume,
            resume_score=82,
            missing_sections=['projects'],
            suggestions=['Add measurable project outcomes.'],
        )
        self.other_resume_analysis = ResumeAnalysis.objects.create(
            resume=self.other_resume,
            resume_score=91,
        )
        self.match_result = JDMatchResult.objects.create(
            resume=self.resume,
            job_description=self.job_description,
            resume_analysis=self.resume_analysis,
            match_score=88,
            matched_skills=['Python'],
            missing_skills=['Django'],
            reason='Strong backend alignment.',
        )
        self.other_match_result = JDMatchResult.objects.create(
            resume=self.other_resume,
            job_description=self.other_job_description,
            resume_analysis=self.other_resume_analysis,
            match_score=99,
        )
        self.question = InterviewQuestion.objects.create(
            match_result=self.match_result,
            question_type=InterviewQuestion.TECHNICAL,
            question='How have you used Django in production?',
        )

    def test_report_list_requires_login(self):
        response = self.client.get(reverse('report_list'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('report_list')}",
        )

    def test_report_list_shows_only_logged_in_users_results(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('report_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/report_list.html')
        self.assertContains(response, 'Resume')
        self.assertContains(response, 'Job Title')
        self.assertContains(response, 'Match Score')
        self.assertContains(response, 'Resume Score')
        self.assertContains(response, 'Created Date')
        self.assertContains(response, 'Owner Resume')
        self.assertContains(response, 'Backend Developer')
        self.assertContains(response, '88.0%')
        self.assertContains(response, '82.0%')
        self.assertNotContains(response, 'Other Resume')
        self.assertNotContains(response, '99.0%')

    def test_report_detail_shows_owned_result(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'report_detail',
                kwargs={'match_result_id': self.match_result.id},
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/report_detail.html')
        self.assertContains(response, 'Owner Resume')
        self.assertContains(response, 'Backend Developer')
        self.assertContains(response, 'Download PDF')
        self.assertContains(response, 'Matched Skills')
        self.assertContains(response, 'Missing Skills')
        self.assertContains(response, 'Strong backend alignment.')

    def test_report_detail_does_not_show_another_users_result(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'report_detail',
                kwargs={'match_result_id': self.other_match_result.id},
            ),
        )

        self.assertEqual(response.status_code, 404)

    def test_report_download_requires_login(self):
        response = self.client.get(
            reverse(
                'report_download',
                kwargs={'match_result_id': self.match_result.id},
            ),
        )

        self.assertRedirects(
            response,
            (
                f"{reverse('login')}?next="
                f"{reverse('report_download', kwargs={'match_result_id': self.match_result.id})}"
            ),
        )

    @patch('apps.reports.views.HTML')
    def test_report_download_returns_pdf_for_owned_result(self, mock_html):
        mock_html.return_value.write_pdf.return_value = b'%PDF-1.4 test pdf'
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'report_download',
                kwargs={'match_result_id': self.match_result.id},
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response.content, b'%PDF-1.4 test pdf')
        self.assertIn('attachment; filename=', response['Content-Disposition'])
        rendered_html = mock_html.call_args.kwargs['string']
        self.assertIn('Owner Resume', rendered_html)
        self.assertIn('Backend Developer', rendered_html)
        self.assertIn('82.0%', rendered_html)
        self.assertIn('88.0%', rendered_html)
        self.assertIn('Python', rendered_html)
        self.assertIn('Django', rendered_html)
        self.assertIn('Add measurable project outcomes.', rendered_html)
        self.assertIn('How have you used Django in production?', rendered_html)

    def test_report_download_does_not_allow_another_users_result(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'report_download',
                kwargs={'match_result_id': self.other_match_result.id},
            ),
        )

        self.assertEqual(response.status_code, 404)
