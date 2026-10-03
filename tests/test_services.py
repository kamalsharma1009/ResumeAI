import pytest
from pathlib import Path
from backend.app.services.skill_extractor import skill_extractor
from backend.app.services.ats_scoring import ats_engine
from backend.app.services.job_matcher import job_matcher
from backend.app.services.skill_gap import skill_gap_analyzer
from backend.app.services.career_predictor import career_predictor
from backend.app.services.roadmap_generator import roadmap_generator
from backend.app.services.interview_generator import interview_generator
from backend.app.services.report_generator import report_generator
from backend.app.utils.security import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    pwd = "mypassword123"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_token_creation_and_decoding():
    data = {"sub": "test@example.com", "role": "USER", "id": 42}
    token = create_access_token(data)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "test@example.com"
    assert decoded["role"] == "USER"

def test_skill_extraction():
    sample_text = (
        "Experienced software engineer proficient in Python, FastAPI, Docker, and PostgreSQL. "
        "Built machine learning models using Scikit-learn and pandas. Strong leadership and communication."
    )
    skills_by_cat = skill_extractor.extract_skills(sample_text)
    assert "Programming Languages" in skills_by_cat
    assert "Python" in skills_by_cat["Programming Languages"]
    assert "FastAPI" in skills_by_cat.get("Frameworks & Web", [])
    assert "Docker" in skills_by_cat.get("Cloud & DevOps", [])
    assert "PostgreSQL" in skills_by_cat.get("Databases", [])
    assert "Machine Learning" in skills_by_cat.get("Data Science & AI/ML", [])

def test_ats_scoring_engine():
    parsed_mock = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+919876543210",
        "location": "Bengaluru",
        "total_experience_years": 3.0,
        "education": [{"degree": "MCA", "institution": "National Institute of Technology", "year": "2023"}],
        "experience": [{"title": "Software Engineer", "snippet": "Developed APIs and automated deployment"}],
        "skills": {
            "Programming Languages": ["Python", "SQL"],
            "Frameworks & Web": ["FastAPI", "React"],
            "Cloud & DevOps": ["Docker", "Git"]
        },
        "projects": [{"title": "AI Recruitment Portal", "description": "Designed backend microservices"}],
        "certifications": ["AWS Certified"]
    }
    raw_text = "Jane Doe jane@example.com +919876543210 Python FastAPI Docker SQL React MCA developed engineered accelerated 20% latency"
    
    score = ats_engine.calculate_score(parsed_mock, raw_text)
    assert 50.0 <= score["overall_ats_score"] <= 100.0
    assert "skills_score" in score
    assert "keyword_score" in score
    assert "experience_score" in score

def test_job_matcher():
    raw_text = "Proficient in Python, SQL, Docker, FastAPI and REST APIs with 2 years of backend experience."
    parsed_data = {
        "skills": {
            "Programming Languages": ["Python", "SQL"],
            "Frameworks & Web": ["FastAPI"],
            "Cloud & DevOps": ["Docker"]
        },
        "total_experience_years": 2.0,
        "education": [{"degree": "MCA"}]
    }
    jd = "We are seeking a Python Developer with Docker, SQL, and AWS skills."
    
    match_result = job_matcher.match_resume_to_job(
        resume_raw_text=raw_text,
        resume_parsed_data=parsed_data,
        job_description=jd,
        job_required_skills_str="Python, Docker, SQL, AWS",
        min_experience_req=1.0
    )
    assert match_result["match_score"] > 50.0
    assert "Python" in match_result["matched_skills"]
    assert "AWS" in match_result["missing_skills"]

def test_skill_gap_analysis():
    missing = ["Docker", "Kubernetes", "AWS"]
    gaps = skill_gap_analyzer.analyze_gaps(missing, target_role="Backend Developer")
    assert len(gaps) == 3
    assert gaps[0]["importance"] in ["Critical", "High"]
    assert "Docker" in [g["missing_skill"] for g in gaps]

def test_career_predictor():
    parsed_data = {
        "skills": {
            "Programming Languages": ["Python", "SQL"],
            "Frameworks & Web": ["FastAPI", "Django"],
            "Cloud & DevOps": ["Docker", "Git"]
        }
    }
    raw = "python developer building backend rest apis with fastapi django sql postgresql docker"
    predictions = career_predictor.predict_roles(parsed_data, raw, top_k=3)
    assert len(predictions) > 0
    top_role = predictions[0]
    assert "confidence_score" in top_role
    assert "explanation" in top_role

def test_roadmap_generator():
    skills = ["Python", "SQL"]
    roadmap = roadmap_generator.generate_roadmap(skills, target_role="Python Developer")
    assert roadmap["target_role"] == "Python Developer"
    assert len(roadmap["phases"]) >= 4

def test_interview_question_generator():
    parsed_data = {
        "skills": {"Programming Languages": ["Python"], "Databases": ["SQL"]},
        "projects": [{"title": "E-Commerce Microservice", "description": "Built using FastAPI and MySQL"}]
    }
    questions = interview_generator.generate_questions(parsed_data, target_role="Python Developer")
    assert len(questions) >= 4
    categories = [q["category"] for q in questions]
    assert "Technical" in categories
    assert "Behavioral" in categories

def test_report_generator_pdf():
    cand_info = {
        "name": "Test Candidate",
        "email": "test@candidate.com",
        "phone": "+919999999999",
        "location": "Bengaluru",
        "total_experience_years": 2.0
    }
    ats = {
        "overall_ats_score": 88.5,
        "skills_score": 85.0,
        "experience_score": 90.0,
        "education_score": 85.0,
        "keyword_score": 80.0,
        "completeness_score": 95.0,
        "formatting_score": 90.0
    }
    skills_by_cat = {
        "Programming Languages": ["Python", "Java"],
        "Cloud & DevOps": ["Docker", "AWS"]
    }
    predicted_roles = [{"role_title": "Python Developer", "confidence_score": 88.0, "explanation": "Strong match"}]
    recs = [{"title": "Quantify Results", "priority": "High", "description": "Add metrics."}]

    pdf_path = report_generator.generate_pdf_report(
        resume_id=999,
        candidate_info=cand_info,
        ats_scores=ats,
        skills_by_category=skills_by_cat,
        predicted_roles=predicted_roles,
        recommendations=recs
    )
    assert Path(pdf_path).exists()
    assert Path(pdf_path).stat().st_size > 1000  # PDF generated with content
