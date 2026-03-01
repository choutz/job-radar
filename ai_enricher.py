import json
from anthropic import Anthropic
from anthropic.types import MessageParam
from models import get_session, Job
from dotenv import load_dotenv
import re

load_dotenv()
client = Anthropic()  # picks up ANTHROPIC_API_KEY from .env automatically

SYSTEM_PROMPT = """You are helping a data scientist evaluate job postings.
Return ONLY valid JSON with no markdown, no code fences, and no explanation."""

USER_PROFILE = """
Experience: ~4 years total
Current target: Mid to Senior individual contributor DS roles only.
Do NOT recommend junior, principal, staff, director, VP, or manager roles.

Location: Remote strongly preferred. Hybrid in Salt Lake City, UT acceptable but less ideal.

RESUME:
Most Recent: Data Scientist - Logistics & Supply Chain, Black Diamond Equipment (Nov 2023 - Oct 2024, SLC UT)
- Built data platform from scratch with SQLite and Python, data warehousing across supply chain
- Time series forecasting for demand prediction and shipping cost optimization
- Dash web app for real-time supply chain analytics
- Automated data pipelines and planning workflow tools
- Collaborated on ERP/data warehouse rebuild

Prior: Software Bio-Mathematician, BioFire Diagnostics (Nov 2020 - Apr 2022, SLC UT)
- Led ML project for next-gen medical diagnostic device, full lifecycle from dataset creation to production
- Managed annotators for custom dataset labeling
- Trained and validated models in Python/scikit-learn, integrated into production device software
- Cross-language validation (MATLAB, Python, C++)

Prior: Systems Engineer, Galil Medical (Dec 2018 - Dec 2019, Minneapolis MN)
- Predictive models from device log files and preclinical data for medical device
- System-level design verification, regulatory documentation

Education: BS Astrophysics + BS Mechanical Engineering + Minor Mathematics, U of Minnesota, 3.46 GPA

Tech: Python (Pandas, NumPy, SciPy, Scikit-learn, PyTorch, SQLAlchemy, Dash, Flask), SQL, R, MATLAB, C++, C#, Git
Skills: Applied math, data engineering, predictive modeling, time series, ML in production
Patents: 2 patents in medical device ablation systems (filed 2021)

INTERESTS (ranked):
1. Supply chain analytics / data science
2. Demand forecasting as part of a broader DS role
3. Medical devices (positive given BioFire / Galil Medical background)
4. Operations research and optimization
5. Time series modeling
6. ML in production

OPEN TO: direct hire, staffing agencies, contract-to-hire
NOT INTERESTED IN: pure MLOps/software engineering with no modeling, onsite or hybrid outside SLC, DoD / defense roles,
roles requiring 6+ years experience, junior/principal/staff/director/manager titles
"""

def get_prompt(job: Job):
    prompt = f"""
{USER_PROFILE}

Here is a job posting:
Title: {job.title}
Company: {job.company}
Description: {job.description[:10000] if job.description else 'N/A'}

Return a JSON object with exactly these fields:
{{
  "relevance_score": <1-10 integer, Penalize if: role requires more years than candidate has, 
  role is junior/principal/staff/director/manager level, role is onsite or hybrid outside SLC. 
  Reward if: supply chain / forecasting / OR / medical devices domain, mid-senior IC level, remote>,
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