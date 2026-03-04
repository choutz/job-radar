import random
import time
from datetime import datetime

from jobspy import scrape_jobs
from sqlalchemy.exc import IntegrityError

from classifier import classify_job
from config import SEARCH_TERMS
from models import get_session, Job, ScrapeRun


def _save_jobs(jobs_df, source, session):
    kept = 0
    for _, row in jobs_df.iterrows():
        try:
            classification = classify_job(row.get("job_url_direct"))

            job = Job(
                title=row.get("title"),
                company=row.get("company"),
                location=row.get("location"),
                is_remote=bool(row.get("is_remote")),
                salary_min=row.get("min_amount"),
                salary_max=row.get("max_amount"),
                salary_interval=row.get("interval"),
                date_posted=str(row.get("date_posted")),
                date_scraped=datetime.now(),
                source=source,
                job_url=row.get("job_url"),
                apply_url=classification["apply_url"],
                apply_type=classification["apply_type"],  # 'reject' is now just a value
                ats_name=classification["ats_name"],
                description=row.get("description"),
            )
            with session.begin_nested():
                session.add(job)
            kept += 1
            print(f"  + {row.get('title')} @ {row.get('company')} [{classification['apply_type']}]")

        except IntegrityError:
            pass
        except Exception as e:
            print(f"  ! Error on row: {e}")

    return kept


def scrape_indeed(term):
    print(f"\nScraping [indeed]: {term}")
    try:
        jobs = scrape_jobs(
            site_name=["indeed"],
            search_term=term,
            location="Remote",
            results_wanted=40,
            hours_old=24 * 14,
            country_indeed="USA",
        )
    except Exception as e:
        print(f"  Scrape failed: {e}")
        return

    print(f"  Raw results: {len(jobs)}")
    with get_session() as session:
        kept = _save_jobs(jobs, "indeed", session)
        session.add(ScrapeRun(
            search_term=f"indeed:{term}",
            ran_at=datetime.now(),
            results_found=len(jobs),
            results_kept=kept,
        ))
        session.commit()
    print(f"  Kept {kept} new jobs")


def scrape_linkedin(term):
    print(f"\nScraping [linkedin]: {term}")
    try:
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=term,
            location="USA",
            is_remote=True,
            results_wanted=40,
            hours_old=24 * 14,
            linkedin_fetch_description=True,
        )
    except Exception as e:
        print(f"  Scrape failed: {e}")
        return

    print(f"  Raw results: {len(jobs)}")
    with get_session() as session:
        kept = _save_jobs(jobs, "linkedin", session)
        session.add(ScrapeRun(
            search_term=f"linkedin:{term}",
            ran_at=datetime.now(),
            results_found=len(jobs),
            results_kept=kept,
        ))
        session.commit()
    print(f"  Kept {kept} new jobs")


def run_scrape():
    for i, term in enumerate(SEARCH_TERMS):
        scrape_indeed(term)
        time.sleep(random.uniform(20, 25))
        scrape_linkedin(term)
        if i < len(SEARCH_TERMS) - 1:
            time.sleep(random.uniform(20, 25))


if __name__ == '__main__':
    run_scrape()


