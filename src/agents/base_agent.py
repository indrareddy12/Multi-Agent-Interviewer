"""
Base agent class for interview agents.
"""
from typing import Dict, Any
from azure_clients import get_chat_llm


class BaseAgent:
    """Base class for all interview agents."""
    
    def __init__(self):
        """Initialize the base agent."""
        self.llm = get_chat_llm()
    
    def generate_question(self, prompt: str) -> str:
        """
        Generate a question using the LLM.
        
        Args:
            prompt: The prompt to use for generation
            
        Returns:
            str: Generated question
        """
        response = self.llm.invoke(prompt)
        return response.content
