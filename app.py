# app.py

import streamlit as st
import pypdf
import io
import re
import plotly.graph_objects as go
from graph import build_recruitment_graph
from agents import comparison_agent

st.set_page_config(
    page_title="🤖 AI HR Recruitment Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI HR Recruitment Assistant")
st.write("Upload multiple resumes and let AI rank the best candidate!")

# ── Helper: extract text from PDF ──
def extract_text(uploaded_file):
    reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
    return "".join(page.extract_text() or "" for page in reader.pages)

# ── Helper: parse score from agent output ──
def parse_total_score(score_text):
    match = re.search(r"TOTAL_SCORE:\s*(\d+)", score_text)
    return int(match.group(1)) if match else 0

# ── Helper: parse individual scores ──
def parse_scores(score_text):
    scores = {
        "Technical Skills": 0,
        "Experience": 0,
        "Education": 0,
        "Job Match": 0
    }
    patterns = {
        "Technical Skills": r"TECHNICAL_SKILLS_SCORE:\s*(\d+)",
        "Experience":       r"EXPERIENCE_SCORE:\s*(\d+)",
        "Education":        r"EDUCATION_SCORE:\s*(\d+)",
        "Job Match":        r"JOB_MATCH_SCORE:\s*(\d+)"
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, score_text)
        if m:
            scores[key] = int(m.group(1))
    return scores

# ── Sidebar — Job Description ──
with st.sidebar:
    st.header("💼 Job Description")
    job_description = st.text_area(
        "Paste job requirements here",
        height=250,
        placeholder="Enter skills needed, experience required..."
    )
    st.divider()
    st.info("💡 Upload 2-3 resumes to compare candidates!")

# ── Main — Resume Upload ──
st.subheader("📄 Upload Resumes (Upload 2 or 3)")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Candidate 1**")
    file1 = st.file_uploader("Upload Resume 1", type=["pdf"], key="r1")

with col2:
    st.markdown("**Candidate 2**")
    file2 = st.file_uploader("Upload Resume 2", type=["pdf"], key="r2")

with col3:
    st.markdown("**Candidate 3 (Optional)**")
    file3 = st.file_uploader("Upload Resume 3", type=["pdf"], key="r3")

# ── Analyze Button ──
if st.button("🚀 Analyze & Compare Candidates", type="primary"):

    uploaded = [f for f in [file1, file2, file3] if f is not None]

    if len(uploaded) < 2:
        st.error("❌ Please upload at least 2 resumes!")
    elif not job_description:
        st.error("❌ Please enter a job description!")
    else:
        candidates = []

        # Process each resume
        progress = st.progress(0, text="Starting analysis...")

        for i, file in enumerate(uploaded):
            st.info(f"🤖 Analyzing Candidate {i+1}: {file.name}...")

            resume_text = extract_text(file)

            graph = build_recruitment_graph()
            result = graph.invoke({
                "resume_text":    resume_text,
                "job_description": job_description,
                "parsed_resume":  "",
                "match_analysis": "",
                "candidate_score": "",
                "final_report":   ""
            })

            total_score = parse_total_score(result["candidate_score"])
            breakdown   = parse_scores(result["candidate_score"])

            candidates.append({
                "name":     file.name.replace(".pdf", ""),
                "score":    total_score,
                "breakdown": breakdown,
                "parsed":   result["parsed_resume"],
                "match":    result["match_analysis"],
                "score_text": result["candidate_score"],
                "report":   result["final_report"]
            })

            progress.progress(
                (i + 1) / len(uploaded),
                text=f"✅ Candidate {i+1} analyzed!"
            )

        # ── Comparison Agent ──
        st.info("🤖 Agent 5: Comparing all candidates...")
        comparison_result = comparison_agent(candidates, job_description)

        st.success("✅ Analysis Complete!")
        st.balloons()

        # ── RANKING BANNER ──
        st.divider()
        st.subheader("🏆 Candidate Ranking")

        sorted_candidates = sorted(
            candidates, key=lambda x: x["score"], reverse=True
        )

        medals = ["🥇", "🥈", "🥉"]
        rank_cols = st.columns(len(sorted_candidates))

        for i, (col, candidate) in enumerate(
            zip(rank_cols, sorted_candidates)
        ):
            with col:
                st.metric(
                    label=f"{medals[i]} Rank {i+1}",
                    value=candidate["name"],
                    delta=f"Score: {candidate['score']}/100"
                )

        # ── SCORE CHART ──
        st.divider()
        st.subheader("📊 Score Comparison Chart")

        fig = go.Figure()
        categories = ["Technical Skills", "Experience",
                      "Education", "Job Match"]
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1",
                  "#96CEB4", "#FFEAA7"]

        for i, candidate in enumerate(candidates):
            fig.add_trace(go.Bar(
                name=candidate["name"],
                x=categories,
                y=[candidate["breakdown"][c] for c in categories],
                marker_color=colors[i]
            ))

        fig.update_layout(
            barmode="group",
            title="Score Breakdown by Category",
            yaxis_title="Score",
            legend_title="Candidates",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── TOTAL SCORE GAUGE ──
        st.subheader("🎯 Total Scores")
        gauge_cols = st.columns(len(candidates))

        for col, candidate in zip(gauge_cols, candidates):
            with col:
                gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=candidate["score"],
                    title={"text": candidate["name"]},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar":  {"color": "#4ECDC4"},
                        "steps": [
                            {"range": [0,  50], "color": "#FF6B6B"},
                            {"range": [50, 75], "color": "#FFEAA7"},
                            {"range": [75, 100], "color": "#96CEB4"}
                        ]
                    }
                ))
                gauge.update_layout(height=250)
                col.plotly_chart(gauge, use_container_width=True)

        # ── AI COMPARISON RESULT ──
        st.divider()
        st.subheader("🤖 AI Comparison & Final Recommendation")
        st.write(comparison_result)

        # ── INDIVIDUAL REPORTS ──
        st.divider()
        st.subheader("📋 Individual Candidate Reports")

        tabs = st.tabs([f"📄 {c['name']}" for c in candidates])

        for tab, candidate in zip(tabs, candidates):
            with tab:
                t1, t2, t3, t4 = st.tabs([
                    "Parsed Resume",
                    "Job Match",
                    "Score",
                    "Full Report"
                ])
                with t1:
                    st.write(candidate["parsed"])
                with t2:
                    st.write(candidate["match"])
                with t3:
                    st.write(candidate["score_text"])
                with t4:
                    st.write(candidate["report"])
                    st.download_button(
                        f"📥 Download {candidate['name']} Report",
                        data=candidate["report"],
                        file_name=f"{candidate['name']}_report.txt",
                        mime="text/plain"
                    )