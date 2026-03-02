import smtplib
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from models import get_session, Job
from dotenv import load_dotenv
from config import EMAIL_ALERT_THRESHOLD

load_dotenv()

SENDER = os.getenv("EMAIL_SENDER")
RECIPIENT = os.getenv("EMAIL_RECIPIENT")
APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_digest():
    # get jobs scored >= threshold scraped in last 24 hours
    cutoff = datetime.now() - timedelta(hours=24)

    with get_session() as session:
        jobs = session.query(Job).filter(
            Job.relevance_score >= EMAIL_ALERT_THRESHOLD,
            Job.date_scraped >= cutoff,
            Job.status != "auto_rejected",
        ).order_by(Job.relevance_score.desc()).all()
        session.expunge_all()

    if not jobs:
        print("No new high-scoring jobs to report")
        return

    # build email body
    body = f"""
<html><body>
<h2>🔍 Job Radar — {len(jobs)} new job{'s' if len(jobs) != 1 else ''} scoring {EMAIL_ALERT_THRESHOLD}+</h2>
<p>{datetime.now().strftime('%B %d, %Y')}</p>
<hr>
"""

    for job in jobs:
        score = job.relevance_score
        emoji = "🟢" if score >= 8 else "🟡"

        salary_str = ""
        if job.salary_min and job.salary_max:
            salary_str = f"${job.salary_min:,.0f}–${job.salary_max:,.0f}"
        elif job.salary_min:
            salary_str = f"${job.salary_min:,.0f}+"

        flags = []
        if job.red_flags:
            try:
                flags = json.loads(job.red_flags) if isinstance(job.red_flags, str) else job.red_flags
            except:
                pass

        body += f"""
<div style="margin-bottom:24px; padding:16px; border:1px solid #ddd; border-radius:8px;">
    <h3 style="margin:0">{emoji} {score}/10 — {job.title}</h3>
    <p style="margin:4px 0; color:#555">{job.company} · {job.location or 'Remote'}</p>
    {"<p style='margin:4px 0'>💰 " + salary_str + "</p>" if salary_str else ""}
    <p style="margin:8px 0"><em>{job.relevance_reason or ''}</em></p>
    {"<p style='margin:4px 0; color:#c00'>⚠️ " + " · ".join(flags) + "</p>" if flags else ""}
    <a href="{job.apply_url}" style="display:inline-block; margin-top:8px; padding:8px 16px; 
       background:#1a73e8; color:white; text-decoration:none; border-radius:4px;">
       Apply Now
    </a>
</div>
"""

    body += "</body></html>"

    # send it
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔍 Job Radar — {len(jobs)} new match{'es' if len(jobs) != 1 else ''} today"
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())

    print(f"Sent digest with {len(jobs)} jobs to {RECIPIENT}")


if __name__ == "__main__":
    send_digest()