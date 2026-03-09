import json
import re
from anthropic import Anthropic
from anthropic.types import MessageParam
from dotenv import load_dotenv
from models import get_session, Job
from models import get_config


load_dotenv()
client = Anthropic()  # picks up ANTHROPIC_API_KEY from .env


def get_prompt(job: Job):
    user_profile = get_config("USER_PROFILE")
    relevance_score_instructions = get_config("RELEVANCE_SCORE_INSTRUCTIONS")

    prompt = f"""
{user_profile}

Here is a job posting:
Title: {job.title}
Company: {job.company}
Description: {job.description[:10000] if job.description else 'N/A'}

Return a JSON object with exactly these fields:
{{
  "relevance_score": {relevance_score_instructions},
  "relevance_reason": <one sentence why>,
  "seniority": <"junior", "mid", "senior", or "staff">,
  "role_type": <e.g. "demand forecasting", "ML engineering", "general DS", "analytics">,
  "years_experience_required": <integer or null, not string>,
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
    system_prompt = get_config("SYSTEM_PROMPT")
    prompt = get_prompt(job)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,  # json response should never exceed this
        messages=[
            MessageParam(role="user", content=prompt)
        ],
        system=system_prompt,
    )

    return parse_json_response(response.content[0].text)


def enrich_pending_jobs(min_score_to_keep: int = 4):
    """Enrich all jobs that haven't been scored yet"""
    with get_session() as session:
        pending = session.query(Job).filter(
            Job.relevance_score.is_(None),
            Job.description.isnot(None),
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


def reenrich_all_jobs(min_score_to_keep: int = 4):
    """Reset and re-score all jobs that have a description, regardless of existing score"""
    with get_session() as session:
        all_jobs = session.query(Job).filter(
            Job.description.isnot(None),
        ).all()
        print(f"Found {len(all_jobs)} jobs to re-score")

        for i, job in enumerate(all_jobs, start=1):
            try:
                job.status = "new"
                result = enrich_job(job)

                job.relevance_score = result["relevance_score"]
                job.relevance_reason = result["relevance_reason"]
                job.seniority = result.get("seniority")
                job.role_type = result.get("role_type")
                job.years_experience_required = result.get("years_experience_required")
                job.key_skills = json.dumps(result.get("key_skills", []))
                job.red_flags = json.dumps(result.get("red_flags", []))

                if job.relevance_score < min_score_to_keep:
                    job.status = "auto_rejected"

                session.commit()
                print(f"  ({i}/{len(all_jobs)}) scored {job.title} @ {job.company} → {job.relevance_score}/10")

            except json.JSONDecodeError as e:
                print(f"  ! ({i}/{len(all_jobs)}) JSON parse error for {job.title}: {e}")
            except Exception as e:
                print(f"  ! ({i}/{len(all_jobs)}) Error enriching {job.title}: {e}")


if __name__ == "__main__":
    # enrich_pending_jobs()
    reenrich_all_jobs()
