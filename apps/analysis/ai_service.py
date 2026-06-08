import json
import os


DEFAULT_AI_INSIGHTS = {
    'summary': '',
    'strengths': [],
    'weaknesses': [],
    'suggestions': [],
    'interview_questions': [],
}


class AIServiceNotConfigured(Exception):
    pass


class AIServiceRequestError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def generate_ai_resume_insights(resume_text, job_description_text):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise AIServiceNotConfigured('OpenAI API key is missing.')

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise AIServiceNotConfigured('OpenAI package is not installed.') from exc

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            response_format={'type': 'json_object'},
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'You analyze resumes against job descriptions. Return only '
                        'valid JSON with these keys: summary, strengths, weaknesses, '
                        'suggestions, interview_questions. Use strings for summary '
                        'and arrays of strings for every other field.'
                    ),
                },
                {
                    'role': 'user',
                    'content': (
                        'Resume text:\n'
                        f'{resume_text or ""}\n\n'
                        'Job description:\n'
                        f'{job_description_text or ""}'
                    ),
                },
            ],
        )
    except Exception as exc:
        raise AIServiceRequestError(_get_openai_error_message(exc)) from exc
    content = response.choices[0].message.content or '{}'

    try:
        insights = json.loads(content)
    except json.JSONDecodeError:
        insights = {}

    return _normalize_ai_insights(insights)


def _normalize_ai_insights(insights):
    normalized = _empty_ai_insights()
    if not isinstance(insights, dict):
        return normalized

    normalized['summary'] = insights.get('summary') or ''
    for key in ('strengths', 'weaknesses', 'suggestions', 'interview_questions'):
        value = insights.get(key) or []
        normalized[key] = value if isinstance(value, list) else [str(value)]

    return normalized


def _empty_ai_insights():
    return {
        'summary': DEFAULT_AI_INSIGHTS['summary'],
        'strengths': [],
        'weaknesses': [],
        'suggestions': [],
        'interview_questions': [],
    }


def _get_openai_error_message(exc):
    error_code = getattr(exc, 'code', None)
    status_code = getattr(exc, 'status_code', None)

    if error_code == 'insufficient_quota':
        return 'OpenAI quota exceeded. Please add billing credits or check your OpenAI plan.'

    if status_code == 401:
        return 'OpenAI API key is invalid. Please update OPENAI_API_KEY.'

    if status_code == 429:
        return 'OpenAI rate limit reached. Please try again later.'

    if exc.__class__.__name__ == 'APIConnectionError':
        return 'Could not connect to OpenAI. Please check your internet connection.'

    return 'AI insights could not be generated right now.'
