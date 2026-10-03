from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ================= AUTH & USERS =================
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: Optional[str] = "USER"  # USER, HR, ADMIN

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ================= SKILLS =================
class SkillItem(BaseModel):
    name: str
    category: str

class SkillGapItem(BaseModel):
    missing_skill: str
    importance: str
    reason: Optional[str] = None
    suggested_learning_path: Optional[str] = None

# ================= RESUMES =================
class ParsedResumeData(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    skills: Dict[str, List[str]] = {}
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    languages: List[str] = []
    achievements: List[str] = []
    total_experience_years: float = 0.0

class ResumeResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    file_type: str
    file_size: int
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_phone: Optional[str] = None
    candidate_experience_years: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True

# ================= ATS & ANALYSIS =================
class ATSScoreBreakdown(BaseModel):
    overall_ats_score: float
    keyword_score: float
    skills_score: float
    experience_score: float
    education_score: float
    completeness_score: float
    formatting_score: float

class ResumeAnalysisResponse(BaseModel):
    id: int
    resume_id: int
    overall_ats_score: float
    keyword_score: float
    skills_score: float
    experience_score: float
    education_score: float
    completeness_score: float
    formatting_score: float
    summary: Optional[str] = None
    predicted_role: Optional[str] = None
    metrics: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True

# ================= JOBS =================
class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    company: str = Field(..., min_length=1, max_length=150)
    description: str = Field(..., min_length=10)
    required_skills: Optional[str] = ""
    preferred_skills: Optional[str] = ""
    min_experience: Optional[float] = 0.0
    education: Optional[str] = ""
    location: Optional[str] = ""

class JobResponse(BaseModel):
    id: int
    user_id: Optional[int]
    title: str
    company: str
    description: str
    required_skills: Optional[str]
    preferred_skills: Optional[str]
    min_experience: float
    education: Optional[str]
    location: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class JobMatchResponse(BaseModel):
    id: Optional[int] = None
    resume_id: int
    job_id: int
    job_title: str
    company: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_match_score: float
    education_match_score: float
    analysis_notes: Optional[str] = None
    created_at: Optional[datetime] = None

# ================= RECOMMENDATIONS & ROADMAPS =================
class RecommendationItem(BaseModel):
    id: Optional[int] = None
    category: str
    title: str
    description: str
    priority: str

class LearningPhase(BaseModel):
    phase: int
    title: str
    duration_weeks: int
    description: str
    topics: List[str]
    projects: List[str]

class LearningRoadmapResponse(BaseModel):
    target_role: str
    summary: str
    phases: List[LearningPhase]

# ================= INTERVIEW QUESTIONS =================
class InterviewQuestionItem(BaseModel):
    id: Optional[int] = None
    category: str  # Technical, HR, Project, Behavioral
    question: str
    difficulty: str  # Easy, Medium, Hard
    topic: Optional[str] = None
    preparation_points: Optional[str] = None

# ================= SCAN HISTORY =================
class ScanHistoryItem(BaseModel):
    id: int
    resume_id: int
    candidate_name: Optional[str] = None
    original_filename: Optional[str] = None
    action: str
    score: Optional[float] = None
    status: str
    details: Optional[str] = None
    created_at: datetime

# ================= DASHBOARD & ANALYTICS =================
class DashboardStats(BaseModel):
    total_resumes: int
    resumes_analyzed: int
    avg_ats_score: float
    avg_job_match: float
    skills_detected: int
    recommended_roles_count: int
    recent_scans: List[Dict[str, Any]]
