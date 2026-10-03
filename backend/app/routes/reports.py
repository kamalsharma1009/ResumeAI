import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    User, Resume, ResumeAnalysis, ResumeSkill, Recommendation, JobMatch, SkillGap
)
from backend.app.auth import get_current_user
from backend.app.services.report_generator import report_generator

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/{resume_id}/download")
def download_pdf_report(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate and return a downloadable, branded PDF analysis report."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume.id).first()
    if not analysis:
        raise HTTPException(status_code=400, detail="Please analyze resume before generating report.")

    parsed_data = json.loads(resume.parsed_data_json) if resume.parsed_data_json else {}
    metrics = json.loads(analysis.metrics_json) if analysis.metrics_json else {}

    # Skills grouped by category
    resume_skills = db.query(ResumeSkill).filter(ResumeSkill.resume_id == resume.id).all()
    skills_by_category = {}
    for s in resume_skills:
        cat = s.category or "Other"
        skills_by_category.setdefault(cat, []).append(s.skill_name)

    # Recommendations
    recs = db.query(Recommendation).filter(Recommendation.resume_id == resume.id).all()
    rec_list = [{"title": r.title, "priority": r.priority, "description": r.description} for r in recs]

    # Latest Job Match
    latest_match = db.query(JobMatch).filter(JobMatch.resume_id == resume.id).order_by(JobMatch.created_at.desc()).first()
    job_match_data = None
    if latest_match and latest_match.job:
        job_match_data = {
            "job_title": latest_match.job.title,
            "company": latest_match.job.company,
            "match_score": latest_match.match_score,
            "matched_skills": json.loads(latest_match.matched_skills_json) if latest_match.matched_skills_json else [],
            "missing_skills": json.loads(latest_match.missing_skills_json) if latest_match.missing_skills_json else []
        }

    ats_scores = {
        "overall_ats_score": analysis.overall_ats_score,
        "keyword_score": analysis.keyword_score,
        "skills_score": analysis.skills_score,
        "experience_score": analysis.experience_score,
        "education_score": analysis.education_score,
        "completeness_score": analysis.completeness_score,
        "formatting_score": analysis.formatting_score
    }

    candidate_info = {
        "name": resume.candidate_name or "Candidate",
        "email": resume.candidate_email or "Not specified",
        "phone": resume.candidate_phone or "Not specified",
        "location": parsed_data.get("location", "Not specified"),
        "total_experience_years": resume.candidate_experience_years
    }

    predicted_roles = metrics.get("predicted_roles", [])

    # Generate PDF
    pdf_path = report_generator.generate_pdf_report(
        resume_id=resume.id,
        candidate_info=candidate_info,
        ats_scores=ats_scores,
        skills_by_category=skills_by_category,
        predicted_roles=predicted_roles,
        recommendations=rec_list,
        job_match=job_match_data,
        target_role=analysis.predicted_role or ""
    )

    clean_cand_name = (resume.candidate_name or "Candidate").replace(" ", "_")
    download_filename = f"Resume_Analysis_Report_{clean_cand_name}.pdf"

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=download_filename
    )
