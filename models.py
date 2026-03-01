from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Session
from datetime import datetime
from pathlib import Path

DATABASE_URL = f"sqlite:///{Path(__file__).parent}/jobs.db"
engine = create_engine(DATABASE_URL, echo=False)

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("company", "title", "date_posted", name="uq_job"),
    )

    id              = Column(Integer, primary_key=True, autoincrement=True)
    title           = Column(String)
    company         = Column(String)
    location        = Column(String)
    is_remote       = Column(Boolean)
    salary_min      = Column(Float)
    salary_max      = Column(Float)
    salary_interval = Column(String)
    date_posted     = Column(String)
    date_scraped    = Column(DateTime, default=datetime.now)
    source          = Column(String)
    job_url         = Column(String)
    apply_url       = Column(String)
    apply_type      = Column(String)  # 'ats', 'company_site'
    ats_name        = Column(String)
    description     = Column(Text)
    status          = Column(String, default="new")  # new, applied, rejected, saved


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
