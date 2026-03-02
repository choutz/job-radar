from scraper import run_scrape
from ai_enricher import enrich_pending_jobs


if __name__ == "__main__":
    run_scrape()
    enrich_pending_jobs()