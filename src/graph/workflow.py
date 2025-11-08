"""
LangGraph workflow for orchestrating the AI interview.
"""
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from config import settings
from config.logging_config import get_logger
from src.agents import TechnicalAgent, HRAgent, ManagerAgent, EvaluationAgent
from src.graph.state import InterviewState, Message, QuestionAnswer

logger = get_logger(__name__)


class InterviewWorkflow:
    """Manages the interview workflow using LangGraph."""
    
    def __init__(self):
        """Initialize the interview workflow."""
        logger.info("Initializing Interview Workflow")
        self.technical_agent = TechnicalAgent()
        self.hr_agent = HRAgent()
        self.manager_agent = ManagerAgent()
        self.evaluation_agent = EvaluationAgent()
        self.graph = self._create_graph()
        logger.info("Interview Workflow initialized successfully")
    
    def _create_graph(self) -> StateGraph:
        """
        Create the LangGraph workflow.
        
        Returns:
            StateGraph: Compiled workflow graph
        """
        # Create the graph
        workflow = StateGraph(InterviewState)
        
        # Add nodes for each agent
        workflow.add_node("technical", self._technical_node)
        workflow.add_node("hr", self._hr_node)
        workflow.add_node("manager", self._manager_node)
        workflow.add_node("evaluation", self._evaluation_node)
        
        # Add conditional edges to determine flow
        workflow.add_conditional_edges(
            "technical",
            self._route_from_technical,
            {
                "hr": "hr",
                "continue": "technical",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "hr",
            self._route_from_hr,
            {
                "manager": "manager",
                "continue": "hr",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "manager",
            self._route_from_manager,
            {
                "evaluation": "evaluation",
                "continue": "manager",
                "end": END
            }
        )
        
        # Evaluation node always ends
        workflow.add_edge("evaluation", END)
        
        # Set entry point
        workflow.set_entry_point("technical")
        
        return workflow.compile()
    
    def _technical_node(self, state: InterviewState) -> InterviewState:
        """
        Technical agent node - asks technical questions.
        
        Args:
            state: Current interview state
            
        Returns:
            InterviewState: Updated state
        """
        logger.info("Technical Agent: Generating question")
        logger.debug(f"Current state - Questions asked: {state['technical_questions_asked']}")
        
        # Generate question
        question = self.technical_agent.ask_question(state)
        logger.info(f"Technical Agent: Question generated (length: {len(question)} chars)")
        
        # Update state
        state["current_question"] = question
        # Don't increment here - we'll increment when answer is processed
        
        # Add to conversation history
        message = Message(
            role="agent",
            content=question,
            agent_type="technical"
        )
        state["conversation_history"].append(message)
        
        return state
    
    def _hr_node(self, state: InterviewState) -> InterviewState:
        """
        HR agent node - asks HR questions.
        
        Args:
            state: Current interview state
            
        Returns:
            InterviewState: Updated state
        """
        logger.info("HR Agent: Generating question")
        logger.debug(f"Current state - Questions asked: {state['hr_questions_asked']}")
        
        # Generate question
        question = self.hr_agent.ask_question(state)
        logger.info(f"HR Agent: Question generated (length: {len(question)} chars)")
        
        # Update state
        state["current_question"] = question
        # Don't increment here - we'll increment when answer is processed
        state["current_agent"] = "hr"
        
        # Add to conversation history
        message = Message(
            role="agent",
            content=question,
            agent_type="hr"
        )
        state["conversation_history"].append(message)
        
        return state
    
    def _manager_node(self, state: InterviewState) -> InterviewState:
        """
        Manager agent node - asks managerial questions.
        
        Args:
            state: Current interview state
            
        Returns:
            InterviewState: Updated state
        """
        logger.info("Manager Agent: Generating question")
        logger.debug(f"Current state - Questions asked: {state['manager_questions_asked']}")
        
        # Generate question
        question = self.manager_agent.ask_question(state)
        logger.info(f"Manager Agent: Question generated (length: {len(question)} chars)")
        
        # Update state
        state["current_question"] = question
        # Don't increment here - we'll increment when answer is processed
        state["current_agent"] = "manager"
        
        # Add to conversation history
        message = Message(
            role="agent",
            content=question,
            agent_type="manager"
        )
        state["conversation_history"].append(message)
        
        return state
    
    def _evaluation_node(self, state: InterviewState) -> InterviewState:
        """
        Evaluation node - generates comprehensive feedback.
        
        Args:
            state: Current interview state
            
        Returns:
            InterviewState: Updated state with evaluation
        """
        logger.info("Evaluation Agent: Starting interview evaluation")
        total_qa_pairs = len(state.get('qa_pairs', []))
        logger.debug(f"Evaluating {total_qa_pairs} Q&A pairs")
        
        # Generate evaluation using the evaluation agent
        evaluation = self.evaluation_agent.generate_evaluation(state)
        
        score = evaluation.get('score', 0)
        logger.info(f"Evaluation Agent: Completed - Score: {score}/100")
        logger.debug(f"Evaluation details - Strengths: {len(evaluation.get('strengths', []))}, "
                    f"Weaknesses: {len(evaluation.get('weaknesses', []))}, "
                    f"Suggestions: {len(evaluation.get('suggestions', []))}")
        
        # Update state
        state["evaluation"] = evaluation
        state["is_complete"] = True
        state["current_agent"] = "evaluation"
        
        return state
    
    def _route_from_technical(
        self, state: InterviewState
    ) -> Literal["hr", "continue", "end"]:
        """
        Determine routing after technical questions.
        
        Args:
            state: Current interview state
            
        Returns:
            str: Next node to visit
        """
        # If we've asked all technical questions, move to HR
        if state["technical_questions_asked"] >= settings.MAX_TECHNICAL_QUESTIONS:
            logger.info(f"Technical round complete ({state['technical_questions_asked']} questions) - Moving to HR")
            return "hr"
        
        # If we just asked a question (current_question is set), stop here
        if state.get("current_question"):
            logger.debug("Technical Agent: Question ready, waiting for answer")
            return "end"
        
        # Otherwise continue with technical questions
        logger.debug("Technical Agent: Continuing with more questions")
        return "continue"
    
    def _route_from_hr(
        self, state: InterviewState
    ) -> Literal["manager", "continue", "end"]:
        """
        Determine routing after HR questions.
        
        Args:
            state: Current interview state
            
        Returns:
            str: Next node to visit
        """
        # If we've asked all HR questions, move to Manager
        if state["hr_questions_asked"] >= settings.MAX_HR_QUESTIONS:
            logger.info(f"HR round complete ({state['hr_questions_asked']} questions) - Moving to Manager")
            return "manager"
        
        # If we just asked a question (current_question is set), stop here
        if state.get("current_question"):
            logger.debug("HR Agent: Question ready, waiting for answer")
            return "end"
        
        # Otherwise continue with HR questions
        logger.debug("HR Agent: Continuing with more questions")
        return "continue"
    
    def _route_from_manager(
        self, state: InterviewState
    ) -> Literal["evaluation", "continue", "end"]:
        """
        Determine routing after manager questions.
        
        Args:
            state: Current interview state
            
        Returns:
            str: Next node to visit
        """
        # If we've asked all manager questions, go to evaluation
        if state["manager_questions_asked"] >= settings.MAX_MANAGER_QUESTIONS:
            logger.info(f"Manager round complete ({state['manager_questions_asked']} questions) - Moving to Evaluation")
            return "evaluation"
        
        # If we just asked a question (current_question is set), stop here
        if state.get("current_question"):
            logger.debug("Manager Agent: Question ready, waiting for answer")
            return "end"
        
        # Otherwise continue with manager questions
        logger.debug("Manager Agent: Continuing with more questions")
        return "continue"
    
    def process_answer(self, state: InterviewState, answer: str) -> InterviewState:
        """
        Process a candidate's answer and update state.
        
        Args:
            state: Current interview state
            answer: Candidate's answer
            
        Returns:
            InterviewState: Updated state
        """
        logger.info(f"Processing answer for {state['current_agent']} agent (length: {len(answer)} chars)")
        
        # Add answer to conversation history
        message = Message(
            role="user",
            content=answer,
            agent_type=None
        )
        state["conversation_history"].append(message)
        
        # Create QA pair and increment question count
        if state["current_question"]:
            qa_pair = QuestionAnswer(
                question=state["current_question"],
                answer=answer,
                agent_type=state["current_agent"]
            )
            state["qa_pairs"].append(qa_pair)
            
            # Increment the appropriate counter based on current agent
            if state["current_agent"] == "technical":
                state["technical_questions_asked"] += 1
                logger.debug(f"Technical questions answered: {state['technical_questions_asked']}")
            elif state["current_agent"] == "hr":
                state["hr_questions_asked"] += 1
                logger.debug(f"HR questions answered: {state['hr_questions_asked']}")
            elif state["current_agent"] == "manager":
                state["manager_questions_asked"] += 1
                logger.debug(f"Manager questions answered: {state['manager_questions_asked']}")
        
        # Clear current question so a new one will be generated
        state["current_question"] = None
        
        # Set last answer for routing
        state["last_answer"] = answer
        
        return state
    
    def run_step(self, state: InterviewState) -> InterviewState:
        """
        Run one step of the interview workflow.
        
        Args:
            state: Current interview state
            
        Returns:
            InterviewState: Updated state after one step
        """
        # Invoke the graph for one step
        result = self.graph.invoke(state)
        return result