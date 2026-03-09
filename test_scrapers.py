"""Quick test to see if glassdoor and ziprecruiter work with jobspy."""
from jobspy import scrape_jobs

SEARCH_TERM = "software engineer"
SITES = ["glassdoor", "zip_recruiter"]

for site in SITES:
    print(f"\nTesting [{site}]...")
    try:
        jobs = scrape_jobs(
            site_name=[site],
            search_term=SEARCH_TERM,
            location="USA",
            is_remote=True,
            results_wanted=40,
            hours_old=24 * 14,
        )
        if jobs is not None and len(jobs) > 0:
            print(f"  OK — got {len(jobs)} results")
            for _, row in jobs.head(3).iterrows():
                print(f"    - {row.get('title')} @ {row.get('company')}")
        else:
            print(f"  FAIL — returned 0 results")
    except Exception as e:
        print(f"  FAIL — {e}")
