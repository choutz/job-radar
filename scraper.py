from jobspy import scrape_jobs
from classifier import classify_job
from models import init_db, get_session, Job, ScrapeRun
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import time
import random

SEARCH_TERMS = [
    "data scientist",
    "remote data scientist",
    "data scientist supply chain"
]


def scrape_one_term(term):
    print(f"\nScraping: {term}")

    try:
        jobs = scrape_jobs(
            site_name=["indeed"],
            search_term=term,
            location="Remote",
            results_wanted=20,
            hours_old=24 * 7,
            country_indeed="USA",
        )
    except Exception as e:
        print(f"  Scrape failed for '{term}': {e}")
        return

    print(f"  Raw results: {len(jobs)}")
    kept = 0

    with get_session() as session:
        for _, row in jobs.iterrows():
            try:
                classification = classify_job(row.get("job_url_direct"))

                if classification["apply_type"] == "reject":
                    continue

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
                    source="indeed",
                    job_url=row.get("job_url"),
                    apply_url=classification["apply_url"],
                    apply_type=classification["apply_type"],
                    ats_name=classification["ats_name"],
                    description=row.get("description"),
                )
                session.add(job)
                # write insert statement, send to db, have constraints checked
                # will throw IntegrityError if duplicate
                session.flush()
                kept += 1
                print(f"  + {row.get('title')} @ {row.get('company')} [{classification['apply_type']}]")

            # handle duplicates
            except IntegrityError as e:
                session.rollback()
                if "uq_job" not in str(e.orig):
                    print(f"  ! Unexpected integrity error: {e.orig}")

            except Exception as e:
                session.rollback()
                print(f"  ! Error on row: {e}")

        session.add(ScrapeRun(
            search_term=term,
            ran_at=datetime.now(),
            results_found=len(jobs),
            results_kept=kept,
        ))
        session.commit()

    print(f"  Kept {kept} new jobs for '{term}'")


def run_scrape():
    init_db()
    for i, term in enumerate(SEARCH_TERMS):
        scrape_one_term(term)
        if i < len(SEARCH_TERMS) - 1:
            delay = random.uniform(8, 15)
            print(f"  Waiting {delay:.1f}s before next term...")
            time.sleep(delay)


if __name__ == '__main__':
    run_scrape()
