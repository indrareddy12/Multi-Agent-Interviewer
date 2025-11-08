"""
State management for the AI Interviewer using LangGraph.
Defines the state structure for the interview workflow.
"""
from typing import TypedDict, List, Dict, Literal, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message in the interview."""
    role: Literal["agent", "user"]
    content: str
    agent_type: Optional[Literal["technical", "hr", "manager"]] = None


class QuestionAnswer(BaseModel):
    """Represents a question-answer pair."""
    question: str
    answer: Optional[str] = None
    agent_type: Literal["technical", "hr", "manager"]


class InterviewState(TypedDict):
    """
    State for the interview workflow.
    
    Attributes:
        candidate_name: Name of the candidate
        job_role: Job role being interviewed for
        experience_level: Experience level (Junior/Mid-Level/Senior)
        resume_text: Optional resume text extracted from uploaded file
        current_agent: Current agent conducting the interview
        technical_questions_asked: Number of technical questions asked
        hr_questions_asked: Number of HR questions asked
        manager_questions_asked: Number of manager questions asked
        conversation_history: List of all messages in the interview
        qa_pairs: List of question-answer pairs
        is_complete: Whether the interview is complete
        current_question: The current question being asked
        last_answer: The last answer provided by the candidate
        evaluation: AI-generated evaluation results (score, feedback, etc.)
    """
    candidate_name: str
    job_role: str
    experience_level: str
    resume_text: Optional[str]
    current_agent: Literal["technical", "hr", "manager", "complete", "evaluation"]
    technical_questions_asked: int
    hr_questions_asked: int
    manager_questions_asked: int
    conversation_history: List[Message]
    qa_pairs: List[QuestionAnswer]
    is_complete: bool
    current_question: Optional[str]
    last_answer: Optional[str]
    evaluation: Optional[Dict]


def create_initial_state(
    candidate_name: str, 
    job_role: str, 
    experience_level: str,
    resume_text: Optional[str] = None
) -> InterviewState:
    """
    Create the initial state for an interview.
    
    Args:
        candidate_name: Name of the candidate
        job_role: Job role being interviewed for
        experience_level: Experience level (Junior/Mid-Level/Senior)
        resume_text: Optional resume text extracted from uploaded file
        
    Returns:
        InterviewState: Initial state for the interview
    """
    return {
        "candidate_name": candidate_name,
        "job_role": job_role,
        "experience_level": experience_level,
        "resume_text": resume_text,
        "current_agent": "technical",
        "technical_questions_asked": 0,
        "hr_questions_asked": 0,
        "manager_questions_asked": 0,
        "conversation_history": [],
        "qa_pairs": [],
        "is_complete": False,
        "current_question": None,
        "last_answer": None,
        "evaluation": None,
    }