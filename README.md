# AI Resume Analyzer

AI Resume Analyzer is a Django web application that helps candidates compare uploaded resumes against job descriptions. It extracts resume text, scores resume completeness, matches required skills, highlights gaps, generates improvement suggestions, creates interview questions, and exports analysis reports as PDFs.

## Overview

The platform is designed for job seekers, students, and placement teams who want a practical way to evaluate resume readiness for a specific role. Users can upload a resume, add job descriptions, run a match analysis, review missing skills and sections, and download a structured report for later reference.

## Features

- User registration, login, logout, and profile pages
- Resume upload and management
- PDF and DOCX resume text extraction
- Job description creation and management
- Resume scoring based on key resume sections
- Skill matching against job description requirements
- Missing skill and missing section detection
- Improvement suggestions for resume optimization
- HR, technical, and project-based interview question generation
- Dashboard with resume, job description, and analysis statistics
- Report listing, report detail pages, and PDF report download
- PostgreSQL-backed data storage

## Tech Stack

- Python
- Django
- PostgreSQL
- HTML templates
- CSS
- Bootstrap
- PyMuPDF for PDF parsing
- python-docx for DOCX parsing
- WeasyPrint for PDF report generation
- python-dotenv for environment variable loading

## Application Workflow

```text
User Login
    ↓
Upload Resume
    ↓
Resume Text Extraction
    ↓
Create Job Description
    ↓
Run Analysis
    ↓
Generate Match Score
    ↓
Identify Matched and Missing Skills
    ↓
Generate Interview Questions
    ↓
Download PDF Report
```

## System Architecture

```text
Browser
    ↓
Django Views
    ↓
Forms and Business Logic Services
    ↓
Django Models
    ↓
PostgreSQL Database
```

Resume processing flow:

```text
Resume Upload
    ↓
PDF/DOCX Text Parser
    ↓
Analysis Engine
    ↓
Report Generator
```

## Screenshots

Add screenshots of the application here after running it locally.

Suggested screenshots:

- Dashboard
- Resume upload page
- Job description form
- Analysis result page
- Interview questions page
- PDF report view

Example:

```md
![Dashboard](screenshots/dashboard.png)
![Analysis Result](screenshots/analysis-result.png)
```

## Installation

1. Clone the repository.

```bash
git clone <repository-url>
cd resume_analyzer
```

2. Create and activate a virtual environment.

```bash
python -m venv env
source env/bin/activate
```

On Windows:

```bash
python -m venv env
env\Scripts\activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

## .env Setup

Create a `.env` file in the project root by copying `.env.example`.

```bash
cp .env.example .env
```

Update the values in `.env` for your local environment.

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
DB_NAME=ai_resume_analyzer
DB_USER=ai_resume_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

Generate a development secret key if needed:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Database Setup

This project uses PostgreSQL. Create a database and user that match your `.env` values.

```sql
CREATE DATABASE ai_resume_analyzer;
CREATE USER ai_resume_user WITH PASSWORD 'your_database_password';
ALTER ROLE ai_resume_user SET client_encoding TO 'utf8';
ALTER ROLE ai_resume_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ai_resume_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ai_resume_analyzer TO ai_resume_user;
```

If you are using PostgreSQL 15 or newer, you may also need to grant schema privileges after connecting to the database:

```sql
\c ai_resume_analyzer
GRANT ALL ON SCHEMA public TO ai_resume_user;
```

## Run Migrations

Apply database migrations:

```bash
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

## Run Server

Start the Django development server:

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

## Project Modules

- `resume_analyzer/` - Django project configuration, settings, URL routing, WSGI, and ASGI setup
- `apps/accounts/` - User authentication, registration, profile views, and account forms
- `apps/resumes/` - Resume upload, resume listing, resume detail views, and PDF/DOCX text extraction
- `apps/jobs/` - Job description CRUD functionality
- `apps/analysis/` - Resume scoring, skill matching, gap analysis, suggestions, dashboard, and interview questions
- `apps/reports/` - Analysis report pages and PDF report generation
- `templates/` - Shared and app-specific Django templates
- `static/` - CSS and static assets
- `media/` - Uploaded resume files during local development

## Database Design

- `User` - Stores authentication and profile information
- `Resume` - Stores uploaded resume files, extracted text, owner, and upload date
- `JobDescription` - Stores job title, company name, experience, required skills, description, and owner
- `ResumeAnalysis` - Stores resume score, detected skills, missing sections, suggestions, and analysis metadata
- `JDMatchResult` - Stores resume-to-job match score, matched skills, missing skills, reasoning, and related analysis
- `InterviewQuestion` - Stores HR, technical, and project-based questions for a match result

## Project Status

Current version: `v1.0`

Completed:

- Authentication
- Resume upload and text extraction
- Resume listing, detail view, and deletion
- Job description creation, editing, listing, and deletion
- Resume scoring and rule-based skill matching
- Missing skill and missing section detection
- Improvement suggestions
- Interview question generation
- Analysis history and reports
- PDF report download

## Future Enhancements

- AI-powered semantic resume and job description matching
- Resume keyword recommendations based on target roles
- Support for additional file formats
- Better analytics for multiple job applications
- Resume version comparison
- Email export and report sharing
- REST API endpoints for external integrations
- Deployment configuration for production environments
- Automated test coverage for all major workflows
- ATS compatibility score
- Cover letter generator
- Recruiter portal
- LinkedIn profile import

## Author

**Nandhini G**  
Backend Developer

Skills: Python, Django, PostgreSQL, REST APIs

- GitHub: https://github.com/G-Nandhini/
- LinkedIn: www.linkedin.com/in/nandhini-g
- Email: gurusamynandhini28@gmail.com

## License

This project is developed for learning, portfolio, and demonstration purposes.
