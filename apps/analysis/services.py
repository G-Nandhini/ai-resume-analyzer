import re

from .models import InterviewQuestion, JDMatchResult, ResumeAnalysis


RESUME_SECTIONS = ('skills', 'experience', 'education', 'projects')


def clean_text(text):
    return re.sub(r'\s+', ' ', (text or '').lower()).strip()


def parse_required_skills(required_skills_text):
    return [
        skill.strip()
        for skill in (required_skills_text or '').split(',')
        if skill.strip()
    ]


def find_matched_skills(resume_text, required_skills):
    cleaned_resume_text = clean_text(resume_text)

    return [
        skill
        for skill in required_skills
        if _contains_skill(cleaned_resume_text, skill)
    ]


def calculate_match_score(matched_skills, required_skills):
    if not required_skills:
        return 0

    return len(matched_skills) / len(required_skills) * 100


def calculate_resume_score(resume_text):
    found_sections = _find_resume_sections(resume_text)

    return len(found_sections) / 6 * 100


def generate_basic_suggestions(resume_text, missing_skills):
    suggestions = []
    missing_sections = _find_missing_resume_sections(resume_text)

    if missing_skills:
        suggestions.append(
            'Add or emphasize these missing skills: '
            f'{", ".join(missing_skills)}.'
        )

    if missing_sections:
        suggestions.append(
            'Add or improve these resume sections: '
            f'{", ".join(missing_sections)}.'
        )

    if not suggestions:
        suggestions.append('Your resume covers the basic required skills and sections.')

    return suggestions


def analyze_resume_against_jd(resume, job_description):
    resume_text = resume.extracted_text or ''
    required_skills = parse_required_skills(job_description.required_skills)
    matched_skills = find_matched_skills(resume_text, required_skills)
    missing_skills = [
        skill
        for skill in required_skills
        if skill not in matched_skills
    ]
    match_score = calculate_match_score(matched_skills, required_skills)
    resume_score = calculate_resume_score(resume_text)
    missing_sections = _find_missing_resume_sections(resume_text)
    suggestions = generate_basic_suggestions(resume_text, missing_skills)

    resume_analysis = ResumeAnalysis.objects.create(
        resume=resume,
        resume_score=resume_score,
        skills_found=matched_skills,
        missing_sections=missing_sections,
        suggestions=suggestions,
    )

    reason = (
        f'Matched {len(matched_skills)} of {len(required_skills)} required skills.'
        if required_skills else
        'No required skills were provided.'
    )

    return JDMatchResult.objects.create(
        resume=resume,
        job_description=job_description,
        resume_analysis=resume_analysis,
        match_score=match_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        reason=reason,
    )


def generate_basic_interview_questions(match_result):
    question_specs = (
        (InterviewQuestion.HR, _build_hr_questions(match_result)),
        (InterviewQuestion.TECHNICAL, _build_technical_questions(match_result)),
        (
            InterviewQuestion.PROJECT_BASED,
            _build_project_based_questions(match_result),
        ),
    )

    for question_type, questions in question_specs:
        existing_count = match_result.interview_questions.filter(
            question_type=question_type,
        ).count()
        questions_to_create = questions[existing_count:5]

        InterviewQuestion.objects.bulk_create([
            InterviewQuestion(
                match_result=match_result,
                question_type=question_type,
                question=question,
            )
            for question in questions_to_create
        ])

    return match_result.interview_questions.all()


def _contains_skill(cleaned_resume_text, skill):
    cleaned_skill = clean_text(skill)

    if not cleaned_skill:
        return False

    if re.fullmatch(r'[\w ]+', cleaned_skill):
        pattern = r'\b' + re.escape(cleaned_skill).replace(r'\ ', r'\s+') + r'\b'
        return re.search(pattern, cleaned_resume_text) is not None

    return cleaned_skill in cleaned_resume_text


def _find_resume_sections(resume_text):
    cleaned_resume_text = clean_text(resume_text)
    found_sections = [
        section
        for section in RESUME_SECTIONS
        if section in cleaned_resume_text
    ]

    if 'email' in cleaned_resume_text or _has_email(resume_text):
        found_sections.append('email')

    if 'phone' in cleaned_resume_text or _has_phone(resume_text):
        found_sections.append('phone')

    return found_sections


def _find_missing_resume_sections(resume_text):
    found_sections = set(_find_resume_sections(resume_text))

    return [
        section
        for section in (*RESUME_SECTIONS, 'email', 'phone')
        if section not in found_sections
    ]


def _has_email(text):
    return re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text or '') is not None


def _has_phone(text):
    return re.search(r'(\+?\d[\d\s().-]{7,}\d)', text or '') is not None


def _build_hr_questions(match_result):
    job_title = match_result.job_description.job_title
    company_name = match_result.job_description.company_name or 'our company'

    return [
        f'Tell me about yourself and why you are interested in the {job_title} role.',
        f'What attracted you to {company_name} and this opportunity?',
        'Describe a time you handled a challenging situation at work.',
        'How do you prioritize your work when multiple deadlines compete?',
        f'What are your short-term career goals for the next role as a {job_title}?',
    ]


def _build_technical_questions(match_result):
    matched_skills = match_result.matched_skills or []
    missing_skills = match_result.missing_skills or []
    primary_matched_skill = (
        matched_skills[0] if matched_skills else 'your strongest technical skill'
    )
    secondary_matched_skill = (
        matched_skills[1] if len(matched_skills) > 1 else primary_matched_skill
    )
    primary_missing_skill = missing_skills[0] if missing_skills else 'a new technology'
    secondary_missing_skill = (
        missing_skills[1] if len(missing_skills) > 1 else primary_missing_skill
    )
    all_skills = matched_skills + missing_skills
    skill_summary = ', '.join(all_skills[:4]) if all_skills else 'the required skills'

    return [
        f'How have you used {primary_matched_skill} in a real project?',
        f'Explain an important concept or best practice in {secondary_matched_skill}.',
        f'How would you approach learning or improving {primary_missing_skill} for this role?',
        (
            f'What would you do if a task required {secondary_missing_skill} '
            'but you had limited experience with it?'
        ),
        f'How would you design or troubleshoot a solution using {skill_summary}?',
    ]


def _build_project_based_questions(match_result):
    job_title = match_result.job_description.job_title
    matched_skills = match_result.matched_skills or []
    primary_skill = matched_skills[0] if matched_skills else 'the relevant skills'
    secondary_skill = matched_skills[1] if len(matched_skills) > 1 else primary_skill

    return [
        f'Walk me through a project that best demonstrates your fit for the {job_title} role.',
        f'Describe a project where you used {primary_skill}. What was your specific contribution?',
        'Tell me about a project challenge you faced and how you solved it.',
        f'How did you measure success or impact in a project involving {secondary_skill}?',
        'If you could improve one past project, what would you change and why?',
    ]
