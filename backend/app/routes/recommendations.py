import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    User, Resume, ResumeAnalysis, Recommendation, LearningRoadmap, InterviewQuestion
)
from backend.app.auth import get_current_user
from backend.app.services.roadmap_generator import roadmap_generator
from backend.app.services.interview_generator import interview_generator

router = APIRouter(prefix="/recommendations", tags=["Recommendations & Career"])

@router.get("/{resume_id}")
def get_recommendations(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve resume improvement suggestions and predicted career roles."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume.id).first()
    metrics = json.loads(analysis.metrics_json) if analysis and analysis.metrics_json else {}

    recs = db.query(Recommendation).filter(Recommendation.resume_id == resume.id).all()
    rec_list = [
        {
            "id": r.id,
            "category": r.category,
            "title": r.title,
            "description": r.description,
            "priority": r.priority
        }
        for r in recs
    ]

    return {
        "resume_id": resume.id,
        "candidate_name": resume.candidate_name,
        "predicted_roles": metrics.get("predicted_roles", []),
        "recommendations": rec_list
    }

@router.get("/{resume_id}/roadmap")
def get_roadmap(
    resume_id: int,
    target_role: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve or dynamically generate a customized learning roadmap."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    # If target_role specified or no existing roadmap, generate one
    existing = db.query(LearningRoadmap).filter(LearningRoadmap.resume_id == resume.id)
    if target_role:
        existing = existing.filter(LearningRoadmap.target_role == target_role)
    roadmap_record = existing.first()

    if roadmap_record:
        return json.loads(roadmap_record.roadmap_json)

    # Generate new roadmap
    parsed_data = json.loads(resume.parsed_data_json) if resume.parsed_data_json else {}
    flat_skills = []
    for s_list in parsed_data.get("skills", {}).values():
        flat_skills.extend(s_list)

    role_to_use = target_role or "Python Developer"
    new_roadmap = roadmap_generator.generate_roadmap(flat_skills, role_to_use)
    
    # Cache in database
    db.add(LearningRoadmap(
        resume_id=resume.id,
        target_role=role_to_use,
        roadmap_json=json.dumps(new_roadmap)
    ))
    db.commit()

    return new_roadmap

@router.get("/{resume_id}/interview")
def get_interview_prep(
    resume_id: int,
    target_role: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve or generate tailored interview questions across categories."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    query = db.query(InterviewQuestion).filter(InterviewQuestion.resume_id == resume.id)
    if target_role:
        query = query.filter(InterviewQuestion.target_role == target_role)
    questions = query.all()

    if not questions:
        # Generate new questions
        parsed_data = json.loads(resume.parsed_data_json) if resume.parsed_data_json else {}
        role = target_role or "Software Engineer"
        generated_qs = interview_generator.generate_questions(parsed_data, role)
        
        saved_qs = []
        for q in generated_qs:
            iq = InterviewQuestion(
                resume_id=resume.id,
                target_role=role,
                category=q["category"],
                question=q["question"],
                difficulty=q["difficulty"],
                topic=q.get("topic"),
                preparation_points=q.get("preparation_points")
            )
            db.add(iq)
            saved_qs.append(iq)
        db.commit()
        questions = saved_qs

    return [
        {
            "id": q.id,
            "category": q.category,
            "question": q.question,
            "difficulty": q.difficulty,
            "topic": q.topic,
            "preparation_points": q.preparation_points
        }
        for q in questions
    ]
