import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

logger = logging.getLogger("uvicorn.error")

def get_engine_and_session(url: str):
    try:
        if url.startswith("sqlite"):
            engine = create_engine(url, connect_args={"check_same_thread": False})
        else:
            engine = create_engine(
                url, 
                pool_pre_ping=True, 
                pool_recycle=3600,
                pool_size=10, 
                max_overflow=20
            )
        # Test connection
        with engine.connect() as conn:
            pass
        return engine
    except Exception as e:
        logger.warning(f"Failed to connect to primary database ({url}): {e}")
        logger.warning("Falling back to local SQLite database for uninterrupted operation.")
        sqlite_url = f"sqlite:///{settings.FRONTEND_DIR.parent}/resume_ai.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = get_engine_and_session(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
