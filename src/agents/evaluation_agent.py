"""
Evaluation Agent for providing comprehensive interview feedback.
"""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.prompts.templates import EVALUATION_AGENT_SYSTEM_PROMPT


class EvaluationAgent(BaseAgent):
    """Agent responsible for evaluating the interview and providing feedback."""
    
    def __init__(self):
        """Initialize the Evaluation Agent."""
        super().__init__()
    
    def generate_evaluation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation based on the entire interview.
        
        Args:
            state: Current interview state with all Q&A pairs
            
        Returns:
            Dict containing score, strengths, weaknesses, and suggestions
        """
        # Build the interview summary
        interview_summary = self._build_interview_summary(state)
        
        # Create the evaluation prompt
        prompt = EVALUATION_AGENT_SYSTEM_PROMPT.format(
            candidate_name=state["candidate_name"],
            job_role=state["job_role"],
            experience_level=state["experience_level"],
            interview_summary=interview_summary
        )
        
        # Get evaluation from LLM
        response = self.llm.invoke(prompt)
        evaluation_text = response.content
        
        # Parse the evaluation (expecting structured format)
        evaluation = self._parse_evaluation(evaluation_text)
        
        return evaluation
    
    def _build_interview_summary(self, state: Dict[str, Any]) -> str:
        """
        Build a comprehensive summary of the interview.
        
        Args:
            state: Interview state
            
        Returns:
            str: Formatted interview summary
        """
        qa_pairs = state.get("qa_pairs", [])
        
        if not qa_pairs:
            return "No interview data available."
        
        summary_parts = []
        
        # Group by agent type
        technical_qa = [qa for qa in qa_pairs if qa.agent_type == "technical"]
        hr_qa = [qa for qa in qa_pairs if qa.agent_type == "hr"]
        manager_qa = [qa for qa in qa_pairs if qa.agent_type == "manager"]
        
        # Technical Round
        if technical_qa:
            summary_parts.append("=== TECHNICAL ROUND ===")
            for i, qa in enumerate(technical_qa, 1):
                summary_parts.append(f"\nQ{i}: {qa.question}")
                summary_parts.append(f"A{i}: {qa.answer or 'No answer provided'}\n")
        
        # HR Round
        if hr_qa:
            summary_parts.append("\n=== HR ROUND ===")
            for i, qa in enumerate(hr_qa, 1):
                summary_parts.append(f"\nQ{i}: {qa.question}")
                summary_parts.append(f"A{i}: {qa.answer or 'No answer provided'}\n")
        
        # Manager Round
        if manager_qa:
            summary_parts.append("\n=== MANAGERIAL ROUND ===")
            for i, qa in enumerate(manager_qa, 1):
                summary_parts.append(f"\nQ{i}: {qa.question}")
                summary_parts.append(f"A{i}: {qa.answer or 'No answer provided'}\n")
        
        return "\n".join(summary_parts)
    
    def _parse_evaluation(self, evaluation_text: str) -> Dict[str, Any]:
        """
        Parse the LLM's evaluation response into structured data.
        
        Args:
            evaluation_text: Raw evaluation text from LLM
            
        Returns:
            Dict with score, strengths, weaknesses, suggestions
        """
        # Initialize default structure
        evaluation = {
            "score": 0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "overall_feedback": ""
        }
        
        # Parse sections
        lines = evaluation_text.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Extract score
            if "SCORE:" in line.upper() or "OVERALL SCORE:" in line.upper():
                try:
                    # Extract number from line (e.g., "Score: 85/100" -> 85)
                    import re
                    score_match = re.search(r'(\d+)', line)
                    if score_match:
                        evaluation["score"] = min(100, max(0, int(score_match.group(1))))
                except:
                    pass
            
            # Identify sections
            elif "STRENGTHS:" in line.upper():
                current_section = "strengths"
            elif "WEAKNESSES:" in line.upper() or "AREAS FOR IMPROVEMENT:" in line.upper():
                current_section = "weaknesses"
            elif "SUGGESTIONS:" in line.upper() or "RECOMMENDATIONS:" in line.upper():
                current_section = "suggestions"
            elif "OVERALL FEEDBACK:" in line.upper() or "SUMMARY:" in line.upper():
                current_section = "overall_feedback"
            
            # Add content to current section
            elif line and current_section:
                # Remove bullet points and clean up
                cleaned_line = line.lstrip('•-*').strip()
                if cleaned_line:
                    if current_section == "overall_feedback":
                        evaluation["overall_feedback"] += cleaned_line + " "
                    elif current_section in ["strengths", "weaknesses", "suggestions"]:
                        evaluation[current_section].append(cleaned_line)
        
        # Ensure we have at least some feedback
        if not evaluation["strengths"] and not evaluation["weaknesses"]:
            evaluation["overall_feedback"] = evaluation_text
        
        return evaluation