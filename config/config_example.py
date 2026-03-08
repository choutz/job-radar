EMAIL_ALERT_THRESHOLD = 6

SEARCH_TERMS = [
    "data scientist",
]

RELEVANCE_SCORE_INSTRUCTIONS = """<1-10 integer, Penalize if: role requires more years than candidate has..."""

SYSTEM_PROMPT = """You are helping a data scientist evaluate job postings.
Return ONLY valid JSON with no markdown, no code fences, and no explanation."""

USER_PROFILE = """
# Paste your background, resume, preferences here
# See README for full instructions
"""