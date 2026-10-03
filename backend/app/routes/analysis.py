import json
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    User, Resume, ResumeAnalysis, ResumeSkill, Recommendation, SkillGap, JobMatch
)
from backend.app.auth import get_current_user
from backend.app.services.ats_scoring import ats_engine
from backend.app.services.career_predictor import career_predictor
from backend.app.services.recommendations import recommendation_engine

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.get("/{resume_id}")
def get_resume_analysis(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get full consolidated analysis for a resume:
    ATS breakdown, skills grouped by category, career role predictions,
    recommendations, recent job matches, and skill gaps.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    if current_user.role == "USER" and resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")

    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not yet completed for this resume.")

    parsed_data = json.loads(resume.parsed_data_json) if resume.parsed_data_json else {}
    metrics = json.loads(analysis.metrics_json) if analysis.metrics_json else {}

    # Fetch skills
    resume_skills = db.query(ResumeSkill).filter(ResumeSkill.resume_id == resume.id).all()
    skills_by_category: Dict[str, list] = {}
    for s in resume_skills:
        cat = s.category or "Other"
        skills_by_category.setdefault(cat, []).append(s.skill_name)

    # Fetch recommendations
    recommendations = db.query(Recommendation).filter(Recommendation.resume_id == resume.id).all()
    rec_list = [
        {
            "id": r.id,
            "category": r.category,
            "title": r.title,
            "description": r.description,
            "priority": r.priority
        }
        for r in recommendations
    ]

    # Fetch latest job match if available
    latest_match = db.query(JobMatch).filter(JobMatch.resume_id == resume.id).order_by(JobMatch.created_at.desc()).first()
    job_match_data = None
    if latest_match:
        job_match_data = {
            "job_id": latest_match.job_id,
            "job_title": latest_match.job.title if latest_match.job else "Target Role",
            "company": latest_match.job.company if latest_match.job else "",
            "match_score": latest_match.match_score,
            "matched_skills": json.loads(latest_match.matched_skills_json) if latest_match.matched_skills_json else [],
            "missing_skills": json.loads(latest_match.missing_skills_json) if latest_match.missing_skills_json else [],
            "analysis_notes": latest_match.analysis_notes
        }

    # Fetch skill gaps
    gaps = db.query(SkillGap).filter(SkillGap.resume_id == resume.id).all()
    gaps_list = [
        {
            "missing_skill": g.missing_skill,
            "importance": g.importance,
            "reason": g.reason,
            "suggested_learning_path": g.suggested_learning_path
        }
        for g in gaps
    ]

    return {
        "resume_id": resume.id,
        "candidate": {
            "name": resume.candidate_name,
            "email": resume.candidate_email,
            "phone": resume.candidate_phone,
            "experience_years": resume.candidate_experience_years,
            "location": parsed_data.get("location", "Not Specified"),
            "original_filename": resume.original_filename
        },
        "ats_breakdown": {
            "overall_ats_score": analysis.overall_ats_score,
            "keyword_score": analysis.keyword_score,
            "skills_score": analysis.skills_score,
            "experience_score": analysis.experience_score,
            "education_score": analysis.education_score,
            "completeness_score": analysis.completeness_score,
            "formatting_score": analysis.formatting_score,
            "predicted_role": analysis.predicted_role
        },
        "parsed_sections": {
            "education": parsed_data.get("education", []),
            "experience": parsed_data.get("experience", []),
            "projects": parsed_data.get("projects", []),
            "certifications": parsed_data.get("certifications", []),
            "achievements": parsed_data.get("achievements", [])
        },
        "skills_by_category": skills_by_category,
        "predicted_roles": metrics.get("predicted_roles", []),
        "recommendations": rec_list,
        "latest_job_match": job_match_data,
        "skill_gaps": gaps_list
    }
