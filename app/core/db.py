# app/core/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

conn_str = (
    "mssql+pyodbc://"
    f"{settings.db_user}:{settings.db_password}@"
    f"{settings.db_server}/{settings.db_name}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)
engine = create_engine(conn_str, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db_connection():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()