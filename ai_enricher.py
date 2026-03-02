import json
import re
from anthropic import Anthropic
from anthropic.types import MessageParam
from dotenv import load_dotenv
from config import SYSTEM_PROMPT, USER_PROFILE, RELEVANCE_SCORE_INSTRUCTIONS
from models import get_session, Job

load_dotenv()
client = Anthropic()  # picks up ANTHROPIC_API_KEY from .env


def get_prompt(job: Job):
    prompt = f"""
{USER_PROFILE}

Here is a job posting:
Title: {job.title}
Company: {job.company}
Description: {job.description[:10000] if job.description else 'N/A'}

Return a JSON object with exactly these fields:
{{
  "relevance_score": {RELEVANCE_SCORE_INSTRUCTIONS},
  "relevance_reason": <one sentence why>,
  "seniority": <"junior", "mid", "senior", or "staff">,
  "role_type": <e.g. "demand forecasting", "ML engineering", "general DS", "analytics">,
  "years_experience_required": <integer or null>,
  "key_skills": <list of up to 5 strings>,
  "red_flags": <list of concerns or empty list>
}}
"""
    return prompt


def parse_json_response(text: str) -> dict:
    # strip markdown code fences if present
    text = re.sub(r'^```json\s*', '', text.strip())
    text = re.sub(r'```$', '', text.strip())
    return json.loads(text.strip())


def enrich_job(job: Job) -> dict:
    prompt = get_prompt(job)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,  # json response should never exceed this
        messages=[
            MessageParam(role="user", content=prompt)
        ],
        system=SYSTEM_PROMPT,
    )

    return parse_json_response(response.content[0].text)


def enrich_pending_jobs(min_score_to_keep: int = 4):
    """Enrich all jobs that haven't been scored yet"""
    with get_session() as session:
        pending = session.query(Job).filter(
            Job.relevance_score == None,
            Job.description != None,
        ).all()

        print(f"Found {len(pending)} unscored jobs")

        for job in pending:
            try:
                result = enrich_job(job)

                job.relevance_score = result["relevance_score"]
                job.relevance_reason = result["relevance_reason"]
                job.seniority = result.get("seniority")
                job.role_type = result.get("role_type")
                job.years_experience_required = result.get("years_experience_required")
                job.key_skills = json.dumps(result.get("key_skills", []))
                job.red_flags = json.dumps(result.get("red_flags", []))

                # auto-reject low relevance jobs
                if job.relevance_score < min_score_to_keep:
                    job.status = "auto_rejected"

                session.commit()
                print(f"  scored {job.title} @ {job.company} → {job.relevance_score}/10")

            except json.JSONDecodeError as e:
                print(f"  ! JSON parse error for {job.title}: {e}")
            except Exception as e:
                print(f"  ! Error enriching {job.title}: {e}")


if __name__ == "__main__":
    enrich_pending_jobs()
