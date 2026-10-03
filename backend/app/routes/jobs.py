import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    User, Job, Resume, JobMatch, SkillGap, ScanHistory, JobSkill, Skill
)
from backend.app.schemas import JobCreate, JobResponse, JobMatchResponse
from backend.app.auth import get_current_user
from backend.app.services.job_matcher import job_matcher
from backend.app.services.skill_gap import skill_gap_analyzer

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting."""
    job = Job(
        user_id=current_user.id,
        title=payload.title.strip(),
        company=payload.company.strip(),
        description=payload.description.strip(),
        required_skills=payload.required_skills.strip() if payload.required_skills else "",
        preferred_skills=payload.preferred_skills.strip() if payload.preferred_skills else "",
        min_experience=payload.min_experience or 0.0,
        education=payload.education.strip() if payload.education else "",
        location=payload.location.strip() if payload.location else "",
        is_active=True
    )
    db.add(job)
    db.flush()

    # Link skills
    if job.required_skills:
        for s in [x.strip() for x in job.required_skills.replace(";", ",").split(",") if x.strip()]:
            db.add(JobSkill(job_id=job.id, skill_name=s, is_required=True))

    db.commit()
    db.refresh(job)
    return job

@router.get("", response_model=List[JobResponse])
def get_jobs(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all active jobs with optional search filtering."""
    query = db.query(Job).filter(Job.is_active == True)
    if search:
        f = f"%{search}%"
        query = query.filter((Job.title.ilike(f)) | (Job.company.ilike(f)) | (Job.location.ilike(f)))
    return query.order_by(Job.created_at.desc()).all()

@router.get("/{job_id:int}", response_model=JobResponse)
def get_job_detail(job_id: int, db: Session = Depends(get_db)):
    """Fetch single job detail."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job

@router.post("/{job_id:int}/quick-match", response_model=JobMatchResponse)
def quick_match_resume(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Match the current user's active resume against this job.
    If the user has not yet uploaded one, evaluates against a demo profile.
    """
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    if not resume:
        resume = db.query(Resume).order_by(Resume.created_at.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="No resume available to match. Please upload a resume first.")
    
    return match_resume_to_job(job_id=job_id, resume_id=resume.id, current_user=current_user, db=db)

@router.post("/{job_id:int}/match/{resume_id:int}", response_model=JobMatchResponse)
def match_resume_to_job(
    job_id: int,
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run AI matching engine between a candidate resume and target job.
    Computes semantic similarity, skill gaps, experience score, and records results.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found.")

    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    parsed_data = json.loads(resume.parsed_data_json) if resume.parsed_data_json else {}

    # Run AI Matching
    match_result = job_matcher.match_resume_to_job(
        resume_raw_text=resume.raw_text or "",
        resume_parsed_data=parsed_data,
        job_description=job.description,
        job_required_skills_str=job.required_skills or "",
        min_experience_req=job.min_experience or 0.0,
        education_req=job.education or ""
    )

    # Save or update JobMatch
    job_match = db.query(JobMatch).filter(
        JobMatch.job_id == job.id,
        JobMatch.resume_id == resume.id
    ).first()

    if not job_match:
        job_match = JobMatch(
            job_id=job.id,
            resume_id=resume.id
        )
        db.add(job_match)

    job_match.match_score = match_result["match_score"]
    job_match.matched_skills_json = json.dumps(match_result["matched_skills"])
    job_match.missing_skills_json = json.dumps(match_result["missing_skills"])
    job_match.experience_match_score = match_result["experience_match_score"]
    job_match.education_match_score = match_result["education_match_score"]
    job_match.analysis_notes = match_result["analysis_notes"]

    # Analyze & Persist Skill Gaps
    db.query(SkillGap).filter(SkillGap.job_id == job.id, SkillGap.resume_id == resume.id).delete()
    gaps = skill_gap_analyzer.analyze_gaps(match_result["missing_skills"], target_role=job.title)
    for g in gaps:
        db.add(SkillGap(
            resume_id=resume.id,
            job_id=job.id,
            missing_skill=g["missing_skill"],
            importance=g["importance"],
            reason=g["reason"],
            suggested_learning_path=g["suggested_learning_path"]
        ))

    # Log in Scan History
    db.add(ScanHistory(
        user_id=current_user.id,
        resume_id=resume.id,
        job_id=job.id,
        action=f"Job Compatibility Match: {job.title}",
        score=match_result["match_score"],
        status="Completed",
        details=f"Matched against {job.company} - {job.title} ({match_result['match_score']}%)"
    ))

    db.commit()
    db.refresh(job_match)

    return JobMatchResponse(
        id=job_match.id,
        resume_id=resume.id,
        job_id=job.id,
        job_title=job.title,
        company=job.company,
        match_score=match_result["match_score"],
        matched_skills=match_result["matched_skills"],
        missing_skills=match_result["missing_skills"],
        experience_match_score=match_result["experience_match_score"],
        education_match_score=match_result["education_match_score"],
        analysis_notes=match_result["analysis_notes"],
        created_at=job_match.created_at
    )

@router.get("/{job_id}/candidates")
def get_job_candidates(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all candidate matches for a job ranked from highest to lowest match score."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    matches = db.query(JobMatch).filter(JobMatch.job_id == job.id).order_by(JobMatch.match_score.desc()).all()
    results = []
    for m in matches:
        resume = m.resume
        results.append({
            "match_id": m.id,
            "resume_id": m.resume_id,
            "candidate_name": resume.candidate_name,
            "candidate_email": resume.candidate_email,
            "experience_years": resume.candidate_experience_years,
            "match_score": m.match_score,
            "matched_skills": json.loads(m.matched_skills_json) if m.matched_skills_json else [],
            "missing_skills": json.loads(m.missing_skills_json) if m.missing_skills_json else [],
            "analysis_notes": m.analysis_notes,
            "date": m.created_at
        })
    return results
