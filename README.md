# AI-Powered Resume Screening, Career Analysis & Recommendation System

**MCA Major Project 2026** - A production-grade intelligent recruitment and career intelligence platform  
Built with **FastAPI · MySQL · Scikit-learn · NLP · ReportLab · HTML/CSS/JS**

---

## Project Overview

This system leverages **Natural Language Processing (NLP)** and **Machine Learning (ML)** to automate the full recruitment pipeline — from resume parsing to personalized career guidance. It provides ATS-style scoring, job compatibility matching, skill gap analysis, career prediction, learning roadmaps, and AI-generated interview preparation.

### Key Highlights
- **Deep Resume Parsing** — Extracts name, email, phone, education, experience, projects, and 100+ tech skills from PDF and DOCX
- **Multi-Factor ATS Scoring** — 6-dimensional algorithm: Skills (30%), Keywords (25%), Experience (20%), Education (15%), Completeness (5%), Formatting (5%)
- **TF-IDF Job Matching** — Cosine similarity engine compares candidate profiles against job descriptions
- **Career Role Prediction** — Heuristic ML classifier predicts top 4 matching roles with confidence scores
- **Skill Gap Analysis** — Priority-tagged missing skills (Critical/High/Medium) for each job match
- **5-Phase Learning Roadmaps** — Auto-generated with timelines, resources, milestones, and capstone projects
- **AI Interview Prep** — Role-specific Technical, HR, Behavioral, and Project questions
- **PDF Executive Report** — Professional ReportLab-generated analysis document
- **Multi-Role System** — Candidate (USER), HR Recruiter, and Admin dashboards
- **JWT Authentication** — Secure bcrypt-hashed passwords + JWT bearer tokens

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend Framework | FastAPI 0.110+ |
| ASGI Server | Uvicorn |
| Database ORM | SQLAlchemy 2.0 |
| Database | MySQL 8.0 via PyMySQL |
| Authentication | JWT (PyJWT) + bcrypt |
| Data Validation | Pydantic v2 |
| Resume Parsing | PyMuPDF (PDF) + python-docx (DOCX) |
| NLP / ML | NLTK, Scikit-learn TF-IDF, regex |
| PDF Generation | ReportLab |
| Frontend | Vanilla HTML5, CSS3, JavaScript |
| Charts | Chart.js (CDN) |
| Config | python-dotenv |

---

## Setup & Installation

### Prerequisites
- Python 3.12+
- MySQL 8.0+ (running locally)
- Git

### Step 1 - Create & Activate Virtual Environment

```
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 2 - Install Dependencies

```
pip install -r backend/requirements.txt
```

### Step 3 - Download NLTK Data

```
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
```

### Step 4 - Configure Environment Variables

Copy the example env file:

```
copy .env.example .env      # Windows
cp .env.example .env        # Linux/macOS
```

Edit `.env` with your MySQL credentials:

```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/resume_ai
SECRET_KEY=your_very_long_random_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=uploads
REPORT_DIR=reports
ENVIRONMENT=development
```

### Step 5 - Create MySQL Database

```sql
CREATE DATABASE resume_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 6 - Run the Application

```
python run.py
```

The server will auto-create all 13 database tables, seed 3 demo accounts, seed 4 sample jobs, and start on http://127.0.0.1:8000

---

## Application URLs

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000 | Landing page |
| http://127.0.0.1:8000/login.html | Login page |
| http://127.0.0.1:8000/register.html | Register new account |
| http://127.0.0.1:8000/dashboard.html | Analytics dashboard |
| http://127.0.0.1:8000/upload.html | Resume upload & AI scan |
| http://127.0.0.1:8000/jobs.html | Job listings management |
| http://127.0.0.1:8000/analysis.html | AI analysis results |
| http://127.0.0.1:8000/recommendations.html | Improvement suggestions |
| http://127.0.0.1:8000/roadmap.html | Learning roadmap |
| http://127.0.0.1:8000/interview.html | Interview prep questions |
| http://127.0.0.1:8000/history.html | Scan history |
| http://127.0.0.1:8000/analytics.html | Advanced analytics |
| http://127.0.0.1:8000/admin.html | Admin panel |
| http://127.0.0.1:8000/docs | Interactive Swagger API docs |
| http://127.0.0.1:8000/redoc | ReDoc API documentation |

---

## Demo Accounts (Auto-seeded on first run)

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| Admin | admin@resumeai.com | admin123 | Full system access |
| HR Recruiter | hr@techcorp.com | hr123456 | All resumes, job management |
| Candidate | john.doe@gmail.com | user123 | Own resumes only |

TIP: The login page has one-click "Demo Login" buttons for each role.

---

## REST API Reference

### Authentication
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login and get JWT token
- GET  /api/auth/me - Get current user profile

### Resumes
- POST   /api/resumes/upload - Upload + auto-analyze resume (PDF/DOCX)
- GET    /api/resumes - List resumes (HR sees all, USER sees own)
- GET    /api/resumes/{id} - Get resume details with full analysis
- DELETE /api/resumes/{id} - Delete resume and physical file

### Jobs
- GET    /api/jobs - List active job postings
- POST   /api/jobs - Create job posting (HR/Admin)
- GET    /api/jobs/{id} - Get job details
- PUT    /api/jobs/{id} - Update job posting
- DELETE /api/jobs/{id} - Delete job posting
- POST   /api/jobs/{id}/match - Match all resumes to job

### Analysis
- GET /api/analysis/{resume_id} - Full AI analysis results
- GET /api/analysis/{resume_id}/skill-gap/{job_id} - Skill gap for specific job
- GET /api/analysis/{resume_id}/matches - All job match scores

### Recommendations & Career
- GET /api/recommendations/{resume_id} - Improvement recommendations
- GET /api/recommendations/{resume_id}/roadmap - 5-phase learning roadmap
- GET /api/recommendations/{resume_id}/interview - Interview questions

### Reports & Analytics
- GET /api/reports/{resume_id}/download - Download PDF report
- GET /api/analytics/dashboard - Dashboard KPIs and chart data

---

## AI/ML Modules

### Resume Parser (resume_parser.py)
- PDF: PyMuPDF text extraction with section detection
- DOCX: python-docx paragraph iteration  
- NLP regex patterns for email, phone, LinkedIn, GitHub
- Degree detection (B.Tech, MCA, MBA, M.Sc, PhD)
- Experience year calculation from date ranges
- Project and technology extraction

### Skill Extractor (skill_extractor.py)
Categorized taxonomy of 100+ skills across:
Programming Languages, Web Frameworks, Databases, Cloud & DevOps, Data Science/ML, Developer Tools

### ATS Scoring Engine (ats_scoring.py)
Six-factor weighted algorithm:
- Skills Coverage: 30%
- Keyword Richness: 25%
- Experience Depth: 20%
- Education Match: 15%
- Profile Completeness: 5%
- Formatting Quality: 5%

### Job Matcher (job_matcher.py)
TF-IDF vectorization + cosine similarity comparison of resume text vs job description.
Output: Match percentage, matched skills list, missing skills list.

### Career Predictor (career_predictor.py)
Heuristic classifier with 12 role profiles. Signal-based scoring from skill categories.
Predicts top-4 roles with confidence percentages.
Supported roles: Python Developer, Full Stack Engineer, Data Scientist, ML Engineer, DevOps Engineer, Java Developer, Frontend Developer, Cloud Architect, Android Developer, UI/UX Designer, Product Manager, Cybersecurity Analyst

### Roadmap Generator (roadmap_generator.py)
5-phase learning path: Foundation, Core Skills, Advanced Topics, Projects, Career Ready.
Includes role-specific resources, milestones, timelines, and capstone project prompts.

### Interview Generator (interview_generator.py)
4 categories: Technical, HR, Behavioral, Project-based.
Difficulty levels: Easy, Medium, Hard. 20+ questions per scan.

### Report Generator (report_generator.py)
Professional PDF via ReportLab including candidate profile, ATS breakdown, skill inventory, predicted roles, job matches, recommendations, and roadmap overview.

---

## Database Schema (13 Tables)

- users - Accounts (roles: USER, HR, ADMIN)
- resumes - Files and parsed data
- resume_analyses - ATS scores and metrics
- skills - Master skill catalog
- resume_skills - Resume-to-skill mapping
- jobs - Job postings
- job_skills - Job required skills
- job_matches - Resume-job similarity scores
- skill_gaps - Missing skills per pair
- scan_history - User activity log
- recommendations - Improvement suggestions
- learning_roadmaps - Career roadmaps
- interview_questions - Generated questions

---

## Security Features

- Passwords: bcrypt hashed (never stored in plain text)
- Authentication: JWT bearer tokens (24 hour default expiry)
- Authorization: Role-based access control (RBAC) on every endpoint
- File Validation: Extension whitelist (.pdf, .docx) + 15MB size limit
- Filename Sanitization: UUID-based renaming prevents path traversal
- CORS: Configured for development
- Secrets: All credentials from .env (never hardcoded)

---

## Configuration Reference (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | mysql+pymysql://root:root@localhost:3306/resume_ai | SQLAlchemy DB URL |
| SECRET_KEY | (required) | JWT signing key |
| ALGORITHM | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | 1440 | Token validity (24h) |
| UPLOAD_DIR | uploads | Resume storage path |
| REPORT_DIR | reports | PDF output path |
| ENVIRONMENT | development | App mode |

---

## Project Requirements Checklist

- Python 3.12+: YES
- FastAPI backend: YES
- MySQL database: YES
- SQLAlchemy ORM: YES
- JWT authentication: YES
- bcrypt password hashing: YES
- Pydantic validation: YES
- python-dotenv config: YES
- HTML/CSS/JS frontend: YES
- Modern responsive UI: YES
- No paid APIs: YES
- Open-source NLP/ML only: YES
- PDF resume parsing: YES
- DOCX resume parsing: YES
- ATS scoring engine: YES
- Job matching (TF-IDF): YES
- Skill gap analysis: YES
- Career role prediction: YES
- Learning roadmap generation: YES
- Interview question generation: YES
- PDF report export: YES
- Multi-role RBAC: YES
- Error handling & validation: YES
- Loading states in UI: YES
- Interactive Swagger docs: YES
- Database auto-seed: YES
- Production architecture: YES

---

Built with FastAPI, MySQL, Scikit-learn, NLTK, ReportLab, and Chart.js
MCA Major Project 2026
