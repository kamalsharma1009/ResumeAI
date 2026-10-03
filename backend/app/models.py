import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, Enum
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="USER", nullable=False)  # USER, HR, ADMIN
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    scan_history = relationship("ScanHistory", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, docx
    file_size = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=True)
    parsed_data_json = Column(Text, nullable=True)
    
    # Quick filter fields
    candidate_name = Column(String(150), nullable=True)
    candidate_email = Column(String(150), nullable=True)
    candidate_phone = Column(String(50), nullable=True)
    candidate_experience_years = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")
    analysis = relationship("ResumeAnalysis", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    skills = relationship("ResumeSkill", back_populates="resume", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="resume", cascade="all, delete-orphan")
    gaps = relationship("SkillGap", back_populates="resume", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="resume", cascade="all, delete-orphan")
    roadmaps = relationship("LearningRoadmap", back_populates="resume", cascade="all, delete-orphan")
    interview_questions = relationship("InterviewQuestion", back_populates="resume", cascade="all, delete-orphan")
    scan_history = relationship("ScanHistory", back_populates="resume", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False, index=True)
    company = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=True)  # Comma or JSON
    preferred_skills = Column(Text, nullable=True)
    min_experience = Column(Float, default=0.0)
    education = Column(String(150), nullable=True)
    location = Column(String(120), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="jobs")
    job_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="job", cascade="all, delete-orphan")


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, unique=True)
    overall_ats_score = Column(Float, nullable=False, default=0.0)
    keyword_score = Column(Float, default=0.0)
    skills_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    completeness_score = Column(Float, default=0.0)
    formatting_score = Column(Float, default=0.0)
    summary = Column(Text, nullable=True)
    metrics_json = Column(Text, nullable=True)
    predicted_role = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="analysis")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(60), nullable=False)  # Technical, Soft Skills, Tools, Cloud, Programming Languages, etc.


class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    skill_name = Column(String(100), nullable=False)
    category = Column(String(60), nullable=True)

    # Relationships
    resume = relationship("Resume", back_populates="skills")
    skill = relationship("Skill")


class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    skill_name = Column(String(100), nullable=False)
    is_required = Column(Boolean, default=True)

    # Relationships
    job = relationship("Job", back_populates="job_skills")
    skill = relationship("Skill")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, nullable=False, default=0.0)
    matched_skills_json = Column(Text, nullable=True)
    missing_skills_json = Column(Text, nullable=True)
    experience_match_score = Column(Float, default=0.0)
    education_match_score = Column(Float, default=0.0)
    analysis_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True)
    missing_skill = Column(String(100), nullable=False)
    importance = Column(String(20), default="High")  # Critical, High, Medium, Low
    reason = Column(Text, nullable=True)
    suggested_learning_path = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="gaps")
    job = relationship("Job", back_populates="skill_gaps")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(60), nullable=False)  # Resume Improvement, Career Role, Skill Expansion
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="Medium")  # High, Medium, Low
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="recommendations")


class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    target_role = Column(String(120), nullable=False)
    roadmap_json = Column(Text, nullable=False)  # JSON structure containing phases & topics
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="roadmaps")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    target_role = Column(String(120), nullable=False)
    category = Column(String(50), nullable=False)  # Technical, HR, Project, Behavioral
    question = Column(Text, nullable=False)
    difficulty = Column(String(20), default="Medium")  # Easy, Medium, Hard
    topic = Column(String(100), nullable=True)
    preparation_points = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="interview_questions")


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(80), nullable=False)  # "Resume Scan", "Job Match Analysis", "Roadmap Generation"
    score = Column(Float, nullable=True)
    status = Column(String(30), default="Completed")  # Completed, Processing, Failed
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="scan_history")
    resume = relationship("Resume", back_populates="scan_history")
