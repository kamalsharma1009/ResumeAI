import re
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from backend.app.config import settings

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal or invalid characters."""
    base_name = os.path.basename(filename)
    # Remove any non-alphanumeric, dot, dash, underscore
    clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', base_name)
    ext = Path(clean_name).suffix.lower()
    stem = Path(clean_name).stem[:50]
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{stem}_{unique_suffix}{ext}"

def validate_file_upload(file: UploadFile) -> str:
    """Validate uploaded resume file extension and return normalized extension."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing or empty."
        )
    
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Only PDF (.pdf) and Word (.docx) files are supported."
        )
    return ext
