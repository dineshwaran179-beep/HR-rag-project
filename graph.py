# graph.py

from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents import (
    resume_parser_agent,
    job_matcher_agent,
    candidate_scorer_agent,
    report_generator_agent
)

class RecruitmentState(TypedDict):
    resume_text: str
    job_description: str
    parsed_resume: str
    match_analysis: str
    candidate_score: str
    final_report: str

def build_recruitment_graph():
    graph = StateGraph(RecruitmentState)

    graph.add_node("resume_parser", resume_parser_agent)
    graph.add_node("job_matcher", job_matcher_agent)
    graph.add_node("candidate_scorer", candidate_scorer_agent)
    graph.add_node("report_generator", report_generator_agent)

    graph.set_entry_point("resume_parser")
    graph.add_edge("resume_parser", "job_matcher")
    graph.add_edge("job_matcher", "candidate_scorer")
    graph.add_edge("candidate_scorer", "report_generator")
    graph.add_edge("report_generator", END)

    return graph.compile()