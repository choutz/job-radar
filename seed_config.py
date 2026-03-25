from models import get_session, Config
from config.config import EMAIL_ALERT_THRESHOLD, SEARCH_TERMS, RELEVANCE_SCORE_INSTRUCTIONS, SYSTEM_PROMPT, USER_PROFILE, COVER_LETTER_NAME, COVER_LETTER_CONTACT
import json

def seed():
    with get_session() as session:
        configs = {
            "EMAIL_ALERT_THRESHOLD": str(EMAIL_ALERT_THRESHOLD),
            "SEARCH_TERMS": json.dumps(SEARCH_TERMS),
            "RELEVANCE_SCORE_INSTRUCTIONS": RELEVANCE_SCORE_INSTRUCTIONS,
            "SYSTEM_PROMPT": SYSTEM_PROMPT,
            "USER_PROFILE": USER_PROFILE,
            "COVER_LETTER_NAME": COVER_LETTER_NAME,
            "COVER_LETTER_CONTACT": COVER_LETTER_CONTACT,
        }
        for key, value in configs.items():
            existing = session.get(Config, key)
            if existing:
                existing.value = value
            else:
                session.add(Config(key=key, value=value))
        session.commit()
        print("Config seeded to DB")

if __name__ == "__main__":
    seed()
