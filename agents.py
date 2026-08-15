# agents.py

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import time

load_dotenv()

def get_llm():
    try:
        import streamlit as st
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        api_key = os.getenv("GROQ_API_KEY")

    return ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=600
    )

# ✅ AGENT 1 — Resume Parser
def resume_parser_agent(state):
    print("🤖 Agent 1: Parsing Resume...")
    time.sleep(3)
    llm = get_llm()

    prompt = f"""
    You are an expert HR Resume Parser.
    Extract the following from the resume clearly:
    1. Full Name
    2. Email & Phone
    3. Years of Experience
    4. Current Job Title
    5. Technical Skills
    6. Education
    7. Previous Companies
    8. Key Achievements
    
    Resume: {state["resume_text"]}
    Give structured output only.
    """

    response = llm.invoke(prompt)
    return {"parsed_resume": response.content}

# ✅ AGENT 2 — Job Matcher
def job_matcher_agent(state):
    print("🤖 Agent 2: Matching Job...")
    time.sleep(3)
    llm = get_llm()

    prompt = f"""
    You are an expert HR Job Matcher.
    Compare resume with job description:
    1. Matching Skills
    2. Missing Skills
    3. Experience Match
    4. Education Match
    5. Match Percentage (0-100%)
    
    Resume: {state["parsed_resume"]}
    Job Description: {state["job_description"]}
    Give detailed analysis only.
    """

    response = llm.invoke(prompt)
    return {"match_analysis": response.content}

# ✅ AGENT 3 — Candidate Scorer
def candidate_scorer_agent(state):
    print("🤖 Agent 3: Scoring...")
    time.sleep(3)
    llm = get_llm()

    prompt = f"""
    You are an expert HR Scorer.
    Score the candidate strictly in this exact format:

    TECHNICAL_SKILLS_SCORE: [number out of 30]
    EXPERIENCE_SCORE: [number out of 25]
    EDUCATION_SCORE: [number out of 20]
    JOB_MATCH_SCORE: [number out of 25]
    TOTAL_SCORE: [number out of 100]
    STRENGTHS: [3 key strengths]
    WEAKNESSES: [3 key weaknesses]
    RECOMMENDATION: [Highly Recommended / Recommended / Not Recommended]

    Resume: {state["parsed_resume"]}
    Match Analysis: {state["match_analysis"]}
    """

    response = llm.invoke(prompt)
    return {"candidate_score": response.content}

# ✅ AGENT 4 — Report Generator
def report_generator_agent(state):
    print("🤖 Agent 4: Generating Report...")
    time.sleep(3)
    llm = get_llm()

    prompt = f"""
    You are an expert HR Report Generator.
    Create a professional HR report with:
    1. Candidate Summary
    2. Job Fit Analysis
    3. Score Breakdown
    4. Strengths & Weaknesses
    5. Interview Recommendation
    6. Top 5 Interview Questions

    Resume: {state["parsed_resume"]}
    Match: {state["match_analysis"]}
    Score: {state["candidate_score"]}
    Give professional report only.
    """

    response = llm.invoke(prompt)
    return {"final_report": response.content}

# ✅ AGENT 5 — Comparison Agent (NEW!)
def comparison_agent(candidates, job_description):
    print("🤖 Agent 5: Comparing All Candidates...")
    time.sleep(3)
    llm = get_llm()

    # Build candidate summaries
    candidate_summaries = ""
    for i, candidate in enumerate(candidates):
        candidate_summaries += f"""
        CANDIDATE {i+1}:
        Score: {candidate['score']}
        Report Summary: {candidate['report'][:300]}
        ---
        """

    prompt = f"""
    You are an expert HR Decision Maker.
    Compare these candidates and rank them:

    {candidate_summaries}

    Job Description: {job_description}

    Provide:
    1. RANKING (1st, 2nd, 3rd best candidate)
    2. WHY each candidate ranked that way
    3. FINAL RECOMMENDATION — who to hire and why
    4. COMPARISON TABLE of all candidates

    Be clear and decisive.
    """

    response = llm.invoke(prompt)
    return response.content