import json
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    User, Resume, ResumeAnalysis, ResumeSkill, Skill, ScanHistory,
    Recommendation, LearningRoadmap, InterviewQuestion
)
from backend.app.schemas import ResumeResponse
from backend.app.config import settings
from backend.app.auth import get_current_user
from backend.app.utils.validators import validate_file_upload, sanitize_filename
from backend.app.services.resume_parser import resume_parser
from backend.app.services.ats_scoring import ats_engine
from backend.app.services.career_predictor import career_predictor
from backend.app.services.recommendations import recommendation_engine
from backend.app.services.roadmap_generator import roadmap_generator
from backend.app.services.interview_generator import interview_generator

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    target_role: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and comprehensively analyze a resume (PDF or DOCX).
    Extracts candidate metadata, computes ATS score, links skills,
    predicts career roles, and generates recommendations.
    """
    ext = validate_file_upload(file)
    safe_name = sanitize_filename(file.filename)
    saved_file_path = settings.UPLOAD_DIR / safe_name

    # Save uploaded bytes
    try:
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {e}"
        )
    finally:
        file.file.close()

    file_size = saved_file_path.stat().st_size
    if file_size > settings.MAX_FILE_SIZE_BYTES:
        saved_file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES / (1024*1024)} MB."
        )

    # 1. Parse text & structure
    try:
        parse_result = resume_parser.parse(str(saved_file_path))
        raw_text = parse_result["raw_text"]
        parsed_data = parse_result["parsed_data"]
    except Exception as e:
        saved_file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse resume: {e}"
        )

    # 2. Persist Resume
    resume = Resume(
        user_id=current_user.id,
        original_filename=file.filename,
        stored_filename=safe_name,
        file_type=ext.replace(".", ""),
        file_size=file_size,
        raw_text=raw_text,
        parsed_data_json=json.dumps(parsed_data),
        candidate_name=parsed_data.get("name"),
        candidate_email=parsed_data.get("email"),
        candidate_phone=parsed_data.get("phone"),
        candidate_experience_years=parsed_data.get("total_experience_years", 0.0)
    )
    db.add(resume)
    db.flush()

    # 3. Calculate ATS Score
    ats_breakdown = ats_engine.calculate_score(parsed_data, raw_text)
    
    # 4. Predict Top Career Roles
    predicted_roles = career_predictor.predict_roles(parsed_data, raw_text, top_k=4)
    top_predicted_role = target_role or (predicted_roles[0]["role_title"] if predicted_roles else "Software Engineer")

    # 5. Persist Analysis Record
    analysis = ResumeAnalysis(
        resume_id=resume.id,
        overall_ats_score=ats_breakdown["overall_ats_score"],
        keyword_score=ats_breakdown["keyword_score"],
        skills_score=ats_breakdown["skills_score"],
        experience_score=ats_breakdown["experience_score"],
        education_score=ats_breakdown["education_score"],
        completeness_score=ats_breakdown["completeness_score"],
        formatting_score=ats_breakdown["formatting_score"],
        predicted_role=top_predicted_role,
        summary=f"Analyzed {len(parsed_data.get('skills', {}))} skill categories with {ats_breakdown['overall_ats_score']}% ATS score.",
        metrics_json=json.dumps({
            "predicted_roles": predicted_roles,
            "ats_breakdown": ats_breakdown
        })
    )
    db.add(analysis)

    # 6. Save Resume Skills
    for category, skill_list in parsed_data.get("skills", {}).items():
        for skill_name in skill_list:
            # Check or create master skill
            master_skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if not master_skill:
                master_skill = Skill(name=skill_name, category=category)
                db.add(master_skill)
                db.flush()
            
            r_skill = ResumeSkill(
                resume_id=resume.id,
                skill_id=master_skill.id,
                skill_name=skill_name,
                category=category
            )
            db.add(r_skill)

    # 7. Generate & Save Improvement Recommendations
    recs = recommendation_engine.generate_recommendations(parsed_data, raw_text)
    for r in recs:
        db.add(Recommendation(
            resume_id=resume.id,
            category=r["category"],
            title=r["title"],
            description=r["description"],
            priority=r["priority"]
        ))

    # 8. Generate & Save Learning Roadmap
    flat_skills = []
    for s_list in parsed_data.get("skills", {}).values():
        flat_skills.extend(s_list)
    roadmap = roadmap_generator.generate_roadmap(flat_skills, top_predicted_role)
    db.add(LearningRoadmap(
        resume_id=resume.id,
        target_role=top_predicted_role,
        roadmap_json=json.dumps(roadmap)
    ))

    # 9. Generate & Save Interview Questions
    interview_qs = interview_generator.generate_questions(parsed_data, top_predicted_role)
    for q in interview_qs:
        db.add(InterviewQuestion(
            resume_id=resume.id,
            target_role=top_predicted_role,
            category=q["category"],
            question=q["question"],
            difficulty=q["difficulty"],
            topic=q.get("topic"),
            preparation_points=q.get("preparation_points")
        ))

    # 10. Record Scan History
    db.add(ScanHistory(
        user_id=current_user.id,
        resume_id=resume.id,
        action="Resume Scan & ATS Evaluation",
        score=ats_breakdown["overall_ats_score"],
        status="Completed",
        details=f"Evaluated against {top_predicted_role} profile."
    ))

    db.commit()
    db.refresh(resume)

    return {
        "message": "Resume uploaded and analyzed successfully.",
        "resume_id": resume.id,
        "candidate_name": resume.candidate_name,
        "ats_score": ats_breakdown["overall_ats_score"],
        "predicted_role": top_predicted_role
    }

@router.post("/demo-scan")
def trigger_demo_scan(
    profile: str = Query("python"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger instant demonstration scan for candidate role (python, data_science, devops, fullstack).
    Enables users and recruiters to immediately test the full analysis pipeline without manual uploads.
    """
    pattern = f"%{profile}%"
    demo_resume = db.query(Resume).filter(
        (Resume.original_filename.ilike(pattern)) |
        (Resume.candidate_name.ilike(pattern)) |
        (Resume.raw_text.ilike(pattern))
    ).first()

    if not demo_resume:
        demo_resume = db.query(Resume).order_by(Resume.id.asc()).first()

    if not demo_resume:
        raise HTTPException(status_code=404, detail="No demo resumes found. Please re-seed data.")

    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == demo_resume.id).first()

    return {
        "message": "Demo profile loaded successfully.",
        "resume_id": demo_resume.id,
        "candidate_name": demo_resume.candidate_name,
        "ats_score": analysis.overall_ats_score if analysis else 85.0,
        "predicted_role": analysis.predicted_role if analysis else "Software Engineer"
    }

@router.get("", response_model=List[ResumeResponse])
def get_resumes(
    search: Optional[str] = Query(None),
    include_demo: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List resumes. HR and ADMIN see all resumes; USER sees their own or demo talent pool if empty."""
    query = db.query(Resume)
    if current_user.role == "USER":
        user_resumes = query.filter(Resume.user_id == current_user.id).all()
        if user_resumes:
            query = query.filter(Resume.user_id == current_user.id)
        elif not include_demo:
            query = query.filter(Resume.user_id == current_user.id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Resume.candidate_name.ilike(search_filter)) |
            (Resume.candidate_email.ilike(search_filter)) |
            (Resume.original_filename.ilike(search_filter))
        )
    
    return query.order_by(Resume.created_at.desc()).all()

@router.get("/{resume_id}")
def get_resume_detail(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full parsed data, analysis, skills, and metrics for a specific resume."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    
    if current_user.role == "USER" and resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this resume.")

    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume.id).first()
    metrics = json.loads(analysis.metrics_json) if analysis and analysis.metrics_json else {}
    parsed_data = json.loads(resume.parsed_data_json) if resume.parsed_data_json else {}

    return {
        "id": resume.id,
        "candidate_name": resume.candidate_name,
        "candidate_email": resume.candidate_email,
        "candidate_phone": resume.candidate_phone,
        "candidate_experience_years": resume.candidate_experience_years,
        "original_filename": resume.original_filename,
        "file_type": resume.file_type,
        "file_size": resume.file_size,
        "created_at": resume.created_at,
        "parsed_data": parsed_data,
        "analysis": {
            "overall_ats_score": analysis.overall_ats_score if analysis else 0.0,
            "keyword_score": analysis.keyword_score if analysis else 0.0,
            "skills_score": analysis.skills_score if analysis else 0.0,
            "experience_score": analysis.experience_score if analysis else 0.0,
            "education_score": analysis.education_score if analysis else 0.0,
            "completeness_score": analysis.completeness_score if analysis else 0.0,
            "formatting_score": analysis.formatting_score if analysis else 0.0,
            "predicted_role": analysis.predicted_role if analysis else "Software Engineer",
            "summary": analysis.summary if analysis else "",
            "metrics": metrics
        }
    }

@router.delete("/{resume_id}", status_code=status.HTTP_200_OK)
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resume and associated physical files."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    
    if current_user.role == "USER" and resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized.")

    # Remove stored physical file
    stored_path = settings.UPLOAD_DIR / resume.stored_filename
    if stored_path.exists():
        stored_path.unlink(missing_ok=True)

    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully."}
