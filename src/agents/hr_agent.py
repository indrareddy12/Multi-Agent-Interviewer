"""
HR Agent for conducting HR interviews.
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from src.prompts.templates import get_agent_prompt
from src.graph.state import InterviewState
from config import settings


class HRAgent(BaseAgent):
    """Agent responsible for asking HR and culture-fit questions."""
    
    def __init__(self):
        """Initialize the HR Agent."""
        super().__init__()
        self.agent_type = "hr"
        self.max_questions = settings.MAX_HR_QUESTIONS
    
    def ask_question(self, state: InterviewState) -> str:
        """
        Generate and ask an HR question.
        
        Args:
            state: Current interview state
            
        Returns:
            str: Generated HR question
        """
        question_number = state["hr_questions_asked"] + 1
        is_first = question_number == 1
        
        # Build conversation history for context
        conversation_history = self._build_conversation_history(
            state["conversation_history"]
        )
        
        # Get the appropriate prompt
        prompt = get_agent_prompt(
            agent_type=self.agent_type,
            candidate_name=state["candidate_name"],
            job_role=state["job_role"],
            experience_level=state["experience_level"],
            question_number=question_number,
            conversation_history=conversation_history,
            is_first_question=is_first,
            resume_text=state.get("resume_text")
        )
        
        # Generate the question
        question = self.generate_question(prompt)
        return question
    
    def _build_conversation_history(self, messages: list) -> str:
        """
        Build a formatted conversation history string.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            str: Formatted conversation history
        """
        if not messages:
            return "No previous conversation."
        
        # Get last 5 messages for context
        recent_messages = messages[-5:]
        history = []
        for msg in recent_messages:
            role = "Interviewer" if msg.role == "agent" else "Candidate"
            history.append(f"{role}: {msg.content}")
        
        return "\n".join(history)