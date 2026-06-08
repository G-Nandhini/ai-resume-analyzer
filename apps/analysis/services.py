import re

from .models import JDMatchResult, ResumeAnalysis


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
