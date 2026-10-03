import os
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from backend.app.database import engine, Base, SessionLocal, get_db
import backend.app.models
from backend.app.models import User, Job, Skill, Resume, ResumeAnalysis, ScanHistory, JobSkill, ResumeSkill, JobMatch, SkillGap, Recommendation, LearningRoadmap, InterviewQuestion
from backend.app.utils.security import hash_password
from backend.app.config import settings
from backend.app.routes import (
    auth, resumes, jobs, analysis, recommendations, reports, analytics
)

from backend.app.seed import seed_full_demo_data

# Seed helper
def seed_initial_database():
    """Ensure database schema is up-to-date and seed default accounts, jobs and rich demo resumes."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_full_demo_data(db)
    except Exception as e:
        print(f"Error during initial seed: {e}")
        db.rollback()
    finally:
        db.close()

# Ensure schema and initial accounts are seeded
try:
    seed_initial_database()
except Exception as _e:
    print(f"Warning during immediate database setup: {_e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        seed_initial_database()
    except Exception as _e:
        print(f"Warning during lifespan database setup: {_e}")
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI-Powered Resume Screening, Career Analysis & Recommendation System (MCA Major Project).",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Favicon handler
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    svg_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
      <defs>
        <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#3b82f6"/>
          <stop offset="100%" stop-color="#06b6d4"/>
        </linearGradient>
      </defs>
      <rect width="100" height="100" rx="24" fill="url(#g)"/>
      <text x="50" y="66" font-family="system-ui, -apple-system, sans-serif" font-size="46" font-weight="900" fill="white" text-anchor="middle">AI</text>
    </svg>"""
    return HTMLResponse(content=svg_icon, media_type="image/svg+xml")

# Register API Routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(resumes.router, prefix=settings.API_PREFIX)
app.include_router(jobs.router, prefix=settings.API_PREFIX)
app.include_router(analysis.router, prefix=settings.API_PREFIX)
app.include_router(recommendations.router, prefix=settings.API_PREFIX)
app.include_router(reports.router, prefix=settings.API_PREFIX)
app.include_router(analytics.router, prefix=settings.API_PREFIX)

# Static file mounts
app.mount("/assets", StaticFiles(directory=str(settings.FRONTEND_DIR / "assets")), name="assets")
app.mount("/reports_download", StaticFiles(directory=str(settings.REPORT_DIR)), name="reports_download")

# Route handler to serve HTML pages
FRONTEND_PAGES = {
    "/": "index.html",
    "/login": "login.html",
    "/register": "register.html",
    "/dashboard": "dashboard.html",
    "/upload": "upload.html",
    "/analysis": "analysis.html",
    "/jobs": "jobs.html",
    "/candidate": "candidate.html",
    "/recommendations": "recommendations.html",
    "/roadmap": "roadmap.html",
    "/interview": "interview.html",
    "/history": "history.html",
    "/analytics": "analytics.html",
    "/report": "report.html",
    "/admin": "admin.html",
}

for route_path, filename in FRONTEND_PAGES.items():
    file_path = settings.FRONTEND_DIR / filename
    def make_handler(f_path):
        async def page_handler():
            if f_path.exists():
                return FileResponse(f_path)
            return HTMLResponse(f"<h3>Page {f_path.name} not found.</h3>", status_code=404)
        return page_handler
    app.add_api_route(route_path, make_handler(file_path), methods=["GET"], include_in_schema=False)

# Catch-all for .html direct requests (e.g. /dashboard.html)
@app.get("/{page_name}.html", include_in_schema=False)
async def serve_html_file(page_name: str):
    file_path = settings.FRONTEND_DIR / f"{page_name}.html"
    if file_path.exists():
        return FileResponse(file_path)
    return HTMLResponse(f"<h3>Page {page_name}.html not found.</h3>", status_code=404)

