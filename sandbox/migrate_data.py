from datetime import datetime
import sqlite3
from models import get_session, Job, ScrapeRun

sqlite_conn = sqlite3.connect("../jobs.db")
sqlite_conn.row_factory = sqlite3.Row
cursor = sqlite_conn.cursor()

cursor.execute("SELECT * FROM jobs")
old_jobs = cursor.fetchall()

cursor.execute("SELECT * FROM scrape_runs")
old_runs = cursor.fetchall()

print(f"Migrating {len(old_jobs)} jobs and {len(old_runs)} scrape runs...")

def parse_dt(val):
    if not val:
        return None
    try:
        return datetime.fromisoformat(val)
    except:
        return None

with get_session() as session:
    for row in old_jobs:
        d = dict(row)
        d["date_scraped"] = parse_dt(d.get("date_scraped"))
        job = Job(**d)
        session.merge(job)

    for row in old_runs:
        d = dict(row)
        d["ran_at"] = parse_dt(d.get("ran_at"))
        run = ScrapeRun(**d)
        session.merge(run)

    session.commit()

print("Done!")
sqlite_conn.close()
