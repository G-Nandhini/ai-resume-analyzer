from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.jobs.models import JobDescription
from apps.resumes.models import Resume

from .ai_service import AIServiceNotConfigured
from .models import InterviewQuestion, JDMatchResult, ResumeAnalysis
from .services import (
    analyze_resume_against_jd,
    calculate_match_score,
    calculate_resume_score,
    clean_text,
    find_matched_skills,
    generate_basic_interview_questions,
    generate_basic_suggestions,
    parse_required_skills,
)


class AnalysisServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='analysis-user',
            password='S3cure-Passphrase-2026',
        )

    def test_clean_text_normalizes_case_and_spacing(self):
        self.assertEqual(clean_text('  Python\nDjango  '), 'python django')

    def test_parse_required_skills_splits_comma_separated_values(self):
        self.assertEqual(
            parse_required_skills('Python, Django, , SQL '),
            ['Python', 'Django', 'SQL'],
        )

    def test_find_matched_skills_is_case_insensitive(self):
        matched_skills = find_matched_skills(
            'Built APIs using python and POSTGRESQL.',
            ['Python', 'Django', 'PostgreSQL'],
        )

        self.assertEqual(matched_skills, ['Python', 'PostgreSQL'])

    def test_calculate_match_score_returns_zero_without_required_skills(self):
        self.assertEqual(calculate_match_score([], []), 0)

    def test_calculate_match_score_uses_required_skill_count(self):
        self.assertEqual(calculate_match_score(['Python'], ['Python', 'Django']), 50)

    def test_calculate_resume_score_checks_basic_sections(self):
        resume_text = (
            'Email: dev@example.com\n'
            'Phone: +1 555 123 4567\n'
            'Skills\nPython\n'
            'Experience\nBuilt systems\n'
            'Education\nBS Computer Science\n'
            'Projects\nResume analyzer'
        )

        self.assertEqual(calculate_resume_score(resume_text), 100)

    def test_generate_basic_suggestions_mentions_missing_skills_and_sections(self):
        suggestions = generate_basic_suggestions(
            'Skills\nPython\nEmail: dev@example.com',
            ['Django'],
        )

        self.assertIn('Django', suggestions[0])
        self.assertIn('experience', suggestions[1])

    def test_analyze_resume_against_jd_saves_analysis_and_match_result(self):
        resume = Resume.objects.create(
            user=self.user,
            title='Backend Resume',
            file='resumes/backend.pdf',
            extracted_text=(
                'Email: dev@example.com\n'
                'Phone: +1 555 123 4567\n'
                'Skills: Python, SQL\n'
                'Experience: Built APIs.'
            ),
        )
        job_description = JobDescription.objects.create(
            user=self.user,
            job_title='Backend Developer',
            required_skills='Python, Django, SQL',
            description='Build backend services.',
        )

        result = analyze_resume_against_jd(resume, job_description)

        self.assertEqual(ResumeAnalysis.objects.count(), 1)
        self.assertEqual(JDMatchResult.objects.count(), 1)
        self.assertEqual(result.resume, resume)
        self.assertEqual(result.job_description, job_description)
        self.assertEqual(result.resume_analysis.resume, resume)
        self.assertEqual(result.matched_skills, ['Python', 'SQL'])
        self.assertEqual(result.missing_skills, ['Django'])
        self.assertAlmostEqual(result.match_score, 66.66666666666666)

    def test_generate_basic_interview_questions_creates_five_of_each_type(self):
        resume = Resume.objects.create(
            user=self.user,
            title='Backend Resume',
            file='resumes/backend.pdf',
            extracted_text='Skills: Python, SQL\nProjects: Built APIs.',
        )
        job_description = JobDescription.objects.create(
            user=self.user,
            job_title='Backend Developer',
            required_skills='Python, Django, SQL',
            description='Build Django apps.',
        )
        result = analyze_resume_against_jd(resume, job_description)

        questions = generate_basic_interview_questions(result)

        self.assertEqual(questions.count(), 15)
        self.assertEqual(
            questions.filter(question_type=InterviewQuestion.HR).count(),
            5,
        )
        self.assertEqual(
            questions.filter(question_type=InterviewQuestion.TECHNICAL).count(),
            5,
        )
        self.assertEqual(
            questions.filter(question_type=InterviewQuestion.PROJECT_BASED).count(),
            5,
        )
        self.assertTrue(
            questions.filter(
                question_type=InterviewQuestion.TECHNICAL,
                question__icontains='Django',
            ).exists(),
        )

    def test_generate_basic_interview_questions_does_not_duplicate_questions(self):
        resume = Resume.objects.create(
            user=self.user,
            title='Backend Resume',
            file='resumes/backend.pdf',
            extracted_text='Skills: Python',
        )
        job_description = JobDescription.objects.create(
            user=self.user,
            job_title='Backend Developer',
            required_skills='Python',
            description='Build services.',
        )
        result = analyze_resume_against_jd(resume, job_description)

        generate_basic_interview_questions(result)
        generate_basic_interview_questions(result)

        self.assertEqual(result.interview_questions.count(), 15)


class AnalyzeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            password='S3cure-Passphrase-2026',
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='S3cure-Passphrase-2026',
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title='Owner Resume',
            file='resumes/owner.pdf',
            extracted_text='Skills: Python\nExperience\nEmail: owner@example.com',
        )
        self.other_resume = Resume.objects.create(
            user=self.other_user,
            title='Other Resume',
            file='resumes/other.pdf',
            extracted_text='Skills: Java',
        )
        self.job_description = JobDescription.objects.create(
            user=self.user,
            job_title='Owner Job',
            required_skills='Python, Django',
            description='Build Django apps.',
        )
        self.other_job_description = JobDescription.objects.create(
            user=self.other_user,
            job_title='Other Job',
            required_skills='Java',
            description='Build Java apps.',
        )

    def test_analyze_form_requires_login(self):
        response = self.client.get(reverse('analyze_form'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('analyze_form')}",
        )

    def test_analyze_form_only_shows_current_users_records(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('analyze_form'))

        self.assertContains(response, self.resume.title)
        self.assertContains(response, self.job_description.job_title)
        self.assertNotContains(response, self.other_resume.title)
        self.assertNotContains(response, self.other_job_description.job_title)

    def test_analyze_form_submit_creates_match_and_redirects_to_result(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('analyze_form'), {
            'resume': self.resume.id,
            'job_description': self.job_description.id,
        })

        result = JDMatchResult.objects.get()
        self.assertEqual(result.resume, self.resume)
        self.assertEqual(result.job_description, self.job_description)
        self.assertRedirects(
            response,
            reverse('analysis_result', kwargs={'match_result_id': result.id}),
            fetch_redirect_response=False,
        )

    def test_analyze_form_rejects_records_owned_by_another_user(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('analyze_form'), {
            'resume': self.other_resume.id,
            'job_description': self.other_job_description.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(JDMatchResult.objects.exists())

    def test_analysis_result_shows_owned_result(self):
        result = analyze_resume_against_jd(self.resume, self.job_description)
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('analysis_result', kwargs={'match_result_id': result.id}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/analysis_result.html')
        self.assertContains(response, self.resume.title)
        self.assertContains(response, self.job_description.job_title)

    def test_generate_ai_insights_without_configuration_shows_message(self):
        result = analyze_resume_against_jd(self.resume, self.job_description)
        self.client.force_login(self.user)

        with patch(
            'apps.analysis.views.generate_ai_resume_insights',
            side_effect=AIServiceNotConfigured,
        ):
            response = self.client.post(
                reverse('generate_ai_insights', kwargs={'match_result_id': result.id}),
                follow=True,
            )

        result.resume_analysis.refresh_from_db()
        self.assertEqual(result.resume_analysis.ai_insights, {})
        self.assertContains(response, 'AI is not configured yet.')

    def test_generate_ai_insights_saves_and_displays_ai_data(self):
        result = analyze_resume_against_jd(self.resume, self.job_description)
        self.client.force_login(self.user)
        ai_insights = {
            'summary': 'Strong backend fit.',
            'strengths': ['Python experience'],
            'weaknesses': ['Limited Django evidence'],
            'suggestions': ['Add Django project details'],
            'interview_questions': ['How have you built Django APIs?'],
        }

        with patch(
            'apps.analysis.views.generate_ai_resume_insights',
            return_value=ai_insights,
        ):
            response = self.client.post(
                reverse('generate_ai_insights', kwargs={'match_result_id': result.id}),
                follow=True,
            )

        result.resume_analysis.refresh_from_db()
        self.assertEqual(result.resume_analysis.ai_insights, ai_insights)
        self.assertContains(response, 'Strong backend fit.')
        self.assertContains(response, 'Python experience')

    def test_analysis_result_does_not_show_another_users_result(self):
        result = analyze_resume_against_jd(self.resume, self.job_description)
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse('analysis_result', kwargs={'match_result_id': result.id}),
        )

        self.assertEqual(response.status_code, 404)

    def test_interview_questions_requires_login(self):
        result = analyze_resume_against_jd(self.resume, self.job_description)

        response = self.client.get(
            reverse('interview_questions', kwargs={'match_result_id': result.id}),
        )

        self.assertRedirects(
            response,
            (
                f"{reverse('login')}?next="
                f"{reverse('interview_questions', kwargs={'match_result_id': result.id})}"
            ),
        )

    def test_latest_interview_questions_redirects_to_latest_owned_result(self):
        result = analyze_resume_against_jd(self.resume, self.job_description)
        self.client.force_login(self.user)

        response = self.client.get(reverse('latest_interview_questions'))

        self.assertRedirects(
            response,
            reverse('interview_questions', kwargs={'match_result_id': result.id}),
            fetch_redirect_response=False,
        )

    def test_latest_interview_questions_redirects_without_results(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('latest_interview_questions'))

        self.assertRedirects(response, reverse('analyze_form'))

    def test_interview_questions_page_generates_and_shows_owned_questions(self):
        result = analyze_resume_against_jd(self.resume, self.job_description)
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('interview_questions', kwargs={'match_result_id': result.id}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/interview_questions.html')
        self.assertContains(response, 'HR Questions')
        self.assertContains(response, 'Technical Questions')
        self.assertContains(response, 'Project Based Questions')
        self.assertEqual(result.interview_questions.count(), 15)

    def test_interview_questions_does_not_show_another_users_result(self):
        result = analyze_resume_against_jd(self.resume, self.job_description)
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse('interview_questions', kwargs={'match_result_id': result.id}),
        )

        self.assertEqual(response.status_code, 404)


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dashboard-owner',
            password='S3cure-Passphrase-2026',
        )
        self.other_user = User.objects.create_user(
            username='dashboard-other',
            password='S3cure-Passphrase-2026',
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title='Owner Resume',
            file='resumes/owner.pdf',
            extracted_text='Skills: Python',
        )
        self.second_resume = Resume.objects.create(
            user=self.user,
            title='Owner Resume Two',
            file='resumes/owner-two.pdf',
            extracted_text='Skills: Django',
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
            required_skills='Python, Django',
            description='Build services.',
        )
        self.other_job_description = JobDescription.objects.create(
            user=self.other_user,
            job_title='Other Developer',
            required_skills='Java',
            description='Build Java services.',
        )
        first_analysis = ResumeAnalysis.objects.create(
            resume=self.resume,
            resume_score=82,
        )
        second_analysis = ResumeAnalysis.objects.create(
            resume=self.second_resume,
            resume_score=74,
        )
        other_analysis = ResumeAnalysis.objects.create(
            resume=self.other_resume,
            resume_score=91,
        )
        JDMatchResult.objects.create(
            resume=self.resume,
            job_description=self.job_description,
            resume_analysis=first_analysis,
            match_score=90,
        )
        JDMatchResult.objects.create(
            resume=self.second_resume,
            job_description=self.job_description,
            resume_analysis=second_analysis,
            match_score=70,
        )
        JDMatchResult.objects.create(
            resume=self.other_resume,
            job_description=self.other_job_description,
            resume_analysis=other_analysis,
            match_score=99,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
        )

    def test_dashboard_shows_current_user_stats_and_recent_analyses(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertEqual(response.context['total_resumes'], 2)
        self.assertEqual(response.context['total_job_descriptions'], 1)
        self.assertEqual(response.context['average_match_score'], 80)
        self.assertEqual(response.context['best_match_score'], 90)
        self.assertContains(response, 'Resume Name')
        self.assertContains(response, 'Job Title')
        self.assertContains(response, 'Owner Resume')
        self.assertContains(response, 'Backend Developer')
        self.assertContains(response, '90.0%')
        self.assertContains(response, '82.0%')
        self.assertNotContains(response, 'Other Resume')
        self.assertNotContains(response, '99.0%')
