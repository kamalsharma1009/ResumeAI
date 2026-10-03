import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "AI-Powered Resume Screening, Career Analysis & Recommendation System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:root@localhost:3306/resume_ai"
    )
    
    # JWT Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_ai_resume_screening_jwt_key_2026_mca_project")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # Paths
    UPLOAD_DIR: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
    REPORT_DIR: Path = BASE_DIR / os.getenv("REPORT_DIR", "reports")
    FRONTEND_DIR: Path = BASE_DIR / "frontend"
    ML_DIR: Path = BASE_DIR / "ml"
    
    # File limits
    MAX_FILE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx"}

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)
(settings.ML_DIR / "models").mkdir(parents=True, exist_ok=True)
