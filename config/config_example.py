"""
SETUP: Copy this file to config/config.py and fill in your details.

    cp config/config_example.py config/config.py

config/config.py is gitignored and will never be committed.
After editing, run `python seed_config.py` to push your changes to the database.
"""


# Minimum relevance score (1-10) to include in the nightly email digest.
EMAIL_ALERT_THRESHOLD = 6


# Search queries passed to JobSpy. Keep this list short — the AI handles
# relevance filtering, so a few broad terms are enough. Too many rapid
# requests can trigger temporary IP blocks.
SEARCH_TERMS = [
    "remote data scientist",
    "remote applied scientist",
]


# Scoring rubric passed to Claude. Defines how 1-10 scores are assigned.
# Customize the disqualifiers, penalties, and rewards to match what matters
# to you (seniority, domain, salary, location policy, etc).
RELEVANCE_SCORE_INSTRUCTIONS = """
Score 1-10. Start at 3 for roles passing disqualifiers. 4-5 is typical, 8-10 requires multiple strong matches.

DISQUALIFIERS (score 1-2):
- <add hard dealbreakers here, e.g. on-site only, PhD required, wrong seniority>

MAJOR PENALTIES (-2 to -3):
- <add strong negatives here, e.g. hybrid, salary below floor, wrong domain>

MINOR PENALTIES (-1):
- <add soft negatives here>

REWARDS (max 10):
+3: <add your highest-value signals, e.g. fully remote>
+2: <add strong positives, e.g. preferred domain>
+1: <add nice-to-haves>
"""


# System prompt sent to Claude before every scoring request.
# Controls output format and model behavior. Customize the role description
# if your use case differs, but keep the JSON output constraint intact.
SYSTEM_PROMPT = """You evaluate job postings for a specific candidate and return a structured assessment.

Your entire response must be a single valid JSON object and nothing else — no markdown, no code fences, no explanation, no assessment before or after the JSON."""


# Your background — work history, skills, and domain experience.
# Claude uses this as context when scoring each job posting.
# Include: years of experience, past roles and what you built, technical skills,
# and domains you've worked in. Do not include preferences or dealbreakers —
# those belong in RELEVANCE_SCORE_INSTRUCTIONS above.
USER_PROFILE = """
Your Name - X years experience, degree(s)

KEY ROLES:
- Company (years): What you built, technologies used, scale/impact
- Company (years): What you built, technologies used, scale/impact

SKILLS: List your core technical skills here

DOMAINS: List the industries or problem areas you've worked in
"""