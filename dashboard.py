import json
import streamlit as st
from models import get_session, Job

st.set_page_config(page_title="Job Refresh", layout="wide")


def check_password():
    if st.session_state.get("authenticated"):
        return True
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if pwd == st.secrets.get("password", "changeme"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password")
    return False


if not check_password():
    st.stop()

# ---- sidebar ----
st.sidebar.title("Filters")
min_score = st.sidebar.slider("Min relevance score", 1, 10, 6)
show_statuses = st.sidebar.multiselect(
    "Show statuses",
    ["new", "saved", "applied", "rejected"],
    default=["new", "saved"]
)
show_auto_rejected = st.sidebar.checkbox("Show auto-rejected", value=False)

# ---- load jobs ----
with get_session() as session:
    statuses = show_statuses + (["auto_rejected"] if show_auto_rejected else [])

    query = session.query(Job).filter(
        Job.relevance_score.isnot(None),
        Job.relevance_score >= min_score,
        Job.status.in_(statuses),
    ).order_by(Job.relevance_score.desc())

    jobs = query.all()
    session.expunge_all()


# ---- header ----
st.title("🔍 Job Refresh")
st.caption(f"{len(jobs)} jobs · score ≥ {min_score} · status: {', '.join(show_statuses)}")

if not jobs:
    st.info("No jobs match your filters.")
    st.stop()

# ---- job cards ----
for job in jobs:
    score = job.relevance_score or 0
    emoji = "🟢" if score >= 8 else "🟡" if score >= 6 else "🔴"
    salary_str = ""
    if job.salary_min and job.salary_max:
        salary_str = f"💰 ${job.salary_min:,.0f}–${job.salary_max:,.0f}"
    elif job.salary_min:
        salary_str = f"💰 ${job.salary_min:,.0f}+"

    ats_str = f"📋 {job.apply_type}" + (f" ({job.ats_name})" if job.ats_name else "")
    header = f"{emoji} **{score}/10** — {job.title} @ {job.company}"
    if salary_str:
        header += f"  |  {salary_str}"

    with st.expander(header):
        col1, col2 = st.columns([3, 1])

        with col1:
            if job.relevance_reason:
                st.markdown(f"**Why:** {job.relevance_reason}")

            if job.red_flags:
                try:
                    flags = json.loads(job.red_flags) if isinstance(job.red_flags, str) else job.red_flags
                    if flags:
                        for f in flags:
                            st.markdown(f"⚠️ {f}")
                except:
                    pass

            meta = [ats_str]
            if job.date_posted:
                meta.append(f"📅 {job.date_posted}")
            if job.location:
                meta.append(f"📍 {job.location}")
            st.caption("  |  ".join(meta))

        with col2:
            if job.apply_url:
                st.link_button("🔗 Apply", job.job_url, use_container_width=True)

            current = job.status or "new"
            new_status = st.selectbox(
                "Status",
                ["new", "saved", "applied", "rejected"],
                index=["new", "saved", "applied", "rejected"].index(current) if current in ["new", "saved", "applied",
                                                                                            "rejected"] else 0,
                key=f"status_{job.id}"
            )
            if new_status != current:
                with get_session() as s:
                    j = s.get(Job, job.id)
                    j.status = new_status
                    s.commit()
                st.rerun()
