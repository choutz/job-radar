EMAIL_ALERT_THRESHOLD = 6

SEARCH_TERMS = [
    "remote data scientist",
    "data scientist supply chain"
]

RELEVANCE_SCORE_INSTRUCTIONS = """<1-10 integer, Penalize if: role requires more years than candidate has, 
role is junior/principal/staff/director/manager level, role is onsite or hybrid outside SLC. 
Reward if: supply chain / forecasting / OR / medical devices domain, mid-senior IC level, remote>"""

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
