#!/usr/bin/env python
"""
Startup script for AI-Powered Resume Screening, Career Analysis & Recommendation System
Launches Uvicorn with FastAPI backend and serves static frontend.
"""

import sys
import uvicorn
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    print("=" * 70)
    print(" AI-Powered Resume Screening, Career Analysis & Recommendation System")
    print(" MCA Major Project 2026")
    print("=" * 70)
    print(" Starting Web Server on: http://127.0.0.1:8000")
    print(" Interactive API Docs:   http://127.0.0.1:8000/docs")
    print("=" * 70)

    uvicorn.run(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
