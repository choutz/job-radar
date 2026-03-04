from urllib.parse import urlparse

# Known ATS domains — expand this over time
ATS_DOMAINS = {
    "greenhouse.io": "Greenhouse",
    "lever.co": "Lever",
    "myworkdayjobs.com": "Workday",
    "bamboohr.com": "BambooHR",
    "dayforcehcm.com": "Dayforce",
    "jobvite.com": "Jobvite",
    "icims.com": "iCIMS",
    "smartrecruiters.com": "SmartRecruiters",
    "ashbyhq.com": "Ashby",
    "recruitee.com": "Recruitee",
    "pinpointhq.com": "Pinpoint",
    "jobs.lever.co": "Lever",
    "apply.workable.com": "Workable",
    "hire.withgoogle.com": "Google Hire",
    "taleo.net": "Taleo",
    "successfactors.com": "SAP SuccessFactors",
    "oraclecloud.com": "Oracle HCM",
    "rippling.com": "Rippling",
}

# Domains to always reject
REJECT_DOMAINS = {
    "ziprecruiter.com",
    # "glassdoor.com",
    "linkedin.com",
    "dice.com",
    "monster.com",
    "careerbuilder.com",
    "simplyhired.com",
    "ladders.com",
    "snagajob.com",
    "recruitics.com",  # tracking redirects, unreliable
}


def classify_job(job_url_direct: str) -> dict:
    if not job_url_direct or str(job_url_direct) == "nan":
        return {"apply_type": "unknown", "ats_name": None, "apply_url": None}

    try:
        parsed = urlparse(job_url_direct)
        domain = parsed.netloc.lower().replace("www.", "")
    except Exception:
        return {"apply_type": "unknown", "ats_name": None, "apply_url": job_url_direct}

    # Check for known ATS
    for ats_domain, ats_name in ATS_DOMAINS.items():
        if ats_domain in domain:
            return {"apply_type": "ats", "ats_name": ats_name, "apply_url": job_url_direct}

    # known aggregators — label but don't reject
    for reject in REJECT_DOMAINS:
        if reject in domain:
            return {"apply_type": "aggregator", "ats_name": None, "apply_url": job_url_direct}

    # company site
    return {"apply_type": "company_site", "ats_name": None, "apply_url": job_url_direct}


if __name__ == "__main__":
    test_urls = [
        "https://boards.greenhouse.io/stripe/jobs/123",
        "https://risepoint.wd503.myworkdayjobs.com/en-US/Risepoint/job/123",
        "https://vpl.bamboohr.com/careers/104",
        "https://careers.alvarezandmarsal.com/en/jobs/123",
        "https://recruitics.com/redirect?something",
        "https://www.ziprecruiter.com/jobs/123",
        None,
    ]
    for url in test_urls:
        print(f"{url[:60] if url else 'None':60} → {classify_job(url)}")
