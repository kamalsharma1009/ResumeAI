import json
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models import (
    User, Resume, ResumeAnalysis, Job, JobMatch, ResumeSkill, ScanHistory
)
from backend.app.auth import get_current_user, require_role

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard"])

@router.get("/dashboard")
def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Consolidated analytics for dashboard: KPI cards, distribution buckets,
    skill frequencies, and recent scan logs.
    """
    # 1. Base counts
    total_resumes = db.query(Resume).count()
    analyzed_resumes = db.query(ResumeAnalysis).count()
    
    # 2. Averages
    avg_ats = db.query(func.avg(ResumeAnalysis.overall_ats_score)).scalar() or 0.0
    avg_match = db.query(func.avg(JobMatch.match_score)).scalar() or 0.0
    total_skills_detected = db.query(ResumeSkill).count()

    # 3. ATS Distribution Buckets (<50, 50-69, 70-84, 85-100)
    all_analyses = db.query(ResumeAnalysis.overall_ats_score).all()
    ats_buckets = {"< 50%": 0, "50% - 69%": 0, "70% - 84%": 0, "85% - 100%": 0}
    for (score,) in all_analyses:
        if score < 50:
            ats_buckets["< 50%"] += 1
        elif score < 70:
            ats_buckets["50% - 69%"] += 1
        elif score < 85:
            ats_buckets["70% - 84%"] += 1
        else:
            ats_buckets["85% - 100%"] += 1

    # 4. Job Match Distribution Buckets
    all_matches = db.query(JobMatch.match_score).all()
    match_buckets = {"< 40%": 0, "40% - 60%": 0, "61% - 80%": 0, "81% - 100%": 0}
    for (m_score,) in all_matches:
        if m_score < 40:
            match_buckets["< 40%"] += 1
        elif m_score <= 60:
            match_buckets["40% - 60%"] += 1
        elif m_score <= 80:
            match_buckets["61% - 80%"] += 1
        else:
            match_buckets["81% - 100%"] += 1

    # 5. Top 8 Detected Skills Frequency
    top_skills_query = (
        db.query(ResumeSkill.skill_name, func.count(ResumeSkill.id).label("count"))
        .group_by(ResumeSkill.skill_name)
        .order_by(func.count(ResumeSkill.id).desc())
        .limit(8)
        .all()
    )
    skill_frequency = [{"skill": s[0], "count": s[1]} for s in top_skills_query]

    # 6. Top Recommended Roles
    top_roles_query = (
        db.query(ResumeAnalysis.predicted_role, func.count(ResumeAnalysis.id).label("count"))
        .filter(ResumeAnalysis.predicted_role != None)
        .group_by(ResumeAnalysis.predicted_role)
        .order_by(func.count(ResumeAnalysis.id).desc())
        .limit(5)
        .all()
    )
    top_roles = [{"role": r[0], "count": r[1]} for r in top_roles_query]

    # 7. Recent Scans Table
    if current_user.role == "USER":
        recent_scans_query = db.query(ScanHistory).filter(ScanHistory.user_id == current_user.id).order_by(ScanHistory.created_at.desc()).limit(10).all()
        if not recent_scans_query:
            recent_scans_query = db.query(ScanHistory).order_by(ScanHistory.created_at.desc()).limit(10).all()
    else:
        recent_scans_query = db.query(ScanHistory).order_by(ScanHistory.created_at.desc()).limit(10).all()

    recent_scans = []
    for s in recent_scans_query:
        resume = s.resume
        analysis = resume.analysis if resume else None
        latest_match = db.query(JobMatch).filter(JobMatch.resume_id == s.resume_id).order_by(JobMatch.created_at.desc()).first() if resume else None
        
        recent_scans.append({
            "id": s.id,
            "resume_id": s.resume_id,
            "candidate_name": resume.candidate_name if resume else "Candidate",
            "original_filename": resume.original_filename if resume else "Resume",
            "ats_score": round(analysis.overall_ats_score, 1) if analysis else None,
            "job_match_score": round(latest_match.match_score, 1) if latest_match else None,
            "top_role": analysis.predicted_role if analysis else "Software Engineer",
            "status": s.status,
            "action": s.action,
            "date": s.created_at.strftime("%b %d, %Y %H:%M")
        })

    # 8. Candidate Specific Metrics (when role is USER)
    user_metrics = None
    if current_user.role == "USER":
        u_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
        if not u_resume:
            u_resume = db.query(Resume).order_by(Resume.created_at.desc()).first()
        if u_resume:
            u_analysis = u_resume.analysis
            u_match = db.query(JobMatch).filter(JobMatch.resume_id == u_resume.id).order_by(JobMatch.match_score.desc()).first()
            user_metrics = {
                "resume_id": u_resume.id,
                "candidate_name": u_resume.candidate_name,
                "ats_score": round(u_analysis.overall_ats_score, 1) if u_analysis else 85.0,
                "predicted_role": u_analysis.predicted_role if u_analysis else "Software Engineer",
                "top_job_match": round(u_match.match_score, 1) if u_match else 90.0,
                "target_job": u_match.job.title if (u_match and u_match.job) else "Senior Developer",
                "target_company": u_match.job.company if (u_match and u_match.job) else "TechCorp",
                "skills_count": len(u_resume.skills),
                "skill_gaps_count": len(u_resume.gaps),
                "recommendations_count": len(u_resume.recommendations)
            }

    return {
        "kpi": {
            "total_resumes": total_resumes,
            "resumes_analyzed": analyzed_resumes,
            "avg_ats_score": round(avg_ats, 1),
            "avg_job_match": round(avg_match, 1),
            "skills_detected": total_skills_detected,
            "recommended_roles_count": len(top_roles)
        },
        "charts": {
            "ats_distribution": ats_buckets,
            "job_match_distribution": match_buckets,
            "skill_frequency": skill_frequency,
            "top_roles": top_roles
        },
        "recent_scans": recent_scans,
        "user_metrics": user_metrics
    }

@router.get("/history")
def get_scan_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch complete historical scan logs."""
    query = db.query(ScanHistory)
    if current_user.role == "USER":
        query = query.filter(ScanHistory.user_id == current_user.id)
    
    logs = query.order_by(ScanHistory.created_at.desc()).limit(100).all()
    results = []
    for item in logs:
        resume = item.resume
        results.append({
            "id": item.id,
            "resume_id": item.resume_id,
            "candidate_name": resume.candidate_name if resume else "N/A",
            "original_filename": resume.original_filename if resume else "N/A",
            "action": item.action,
            "score": item.score,
            "status": item.status,
            "details": item.details,
            "date": item.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return results

@router.get("/admin")
def get_admin_overview(
    current_user: User = Depends(require_role(["ADMIN", "HR"])),
    db: Session = Depends(get_db)
):
    """Admin dashboard stats and user management metrics."""
    total_users = db.query(User).count()
    total_resumes = db.query(Resume).count()
    total_jobs = db.query(Job).count()
    total_scans = db.query(ScanHistory).count()

    users_list = db.query(User).order_by(User.created_at.desc()).limit(20).all()
    users_data = [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for u in users_list
    ]

    return {
        "stats": {
            "total_users": total_users,
            "total_resumes": total_resumes,
            "total_jobs": total_jobs,
            "total_scans": total_scans
        },
        "users": users_data
    }

@router.post("/reseed")
def reseed_demo_data(
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin utility: Re-seed full realistic demo candidates, jobs, and analysis records."""
    from backend.app.seed import seed_full_demo_data
    try:
        seed_full_demo_data(db)
        return {"message": "Demo data successfully synchronized and verified."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reseed database: {e}")

