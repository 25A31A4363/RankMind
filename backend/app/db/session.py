import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATA_DIR

DB_PATH = DATA_DIR / "rankmind.db"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# Create SQLite engine with foreign key constraints enabled
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Enforce foreign key constraints in SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency helper for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
