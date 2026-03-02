from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Session
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    # try .env first (local), then streamlit secrets (cloud)
    url = os.getenv("DATABASE_URL")
    if not url:
        try:
            import streamlit as st
            url = st.secrets["DATABASE_URL"]
        except:
            pass
    return url or f"sqlite:///{Path(__file__).parent}/jobs.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{Path(__file__).parent}/jobs.db")
engine = create_engine(DATABASE_URL, echo=False)

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("company", "title", "date_posted", name="uq_job"),
    )

    id                        = Column(Integer, primary_key=True, autoincrement=True)
    title                     = Column(String)
    company                   = Column(String)
    location                  = Column(String)
    is_remote                 = Column(Boolean)
    salary_min                = Column(Float)
    salary_max                = Column(Float)
    salary_interval           = Column(String)
    date_posted               = Column(String)
    date_scraped              = Column(DateTime, default=datetime.now)
    source                    = Column(String)
    job_url                   = Column(String)
    apply_url                 = Column(String)
    apply_type                = Column(String)  # 'ats', 'company_site'
    ats_name                  = Column(String)
    description               = Column(Text)
    status                    = Column(String, default="new")  # new, applied, rejected, saved
    relevance_score           = Column(Integer)
    relevance_reason          = Column(String)
    seniority                 = Column(String)
    role_type                 = Column(String)
    years_experience_required = Column(Integer)
    key_skills                = Column(String)  # stored as JSON string
    red_flags                 = Column(String)  # stored as JSON string


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    search_term    = Column(String)
    ran_at         = Column(DateTime, default=datetime.now)
    results_found  = Column(Integer)
    results_kept   = Column(Integer)


def init_db():
    Base.metadata.create_all(engine)
    print("DB ready")

def get_session() -> Session:
    return Session(engine)
