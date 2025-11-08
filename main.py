"""
Main application entry point for the AI Interviewer.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from config import settings
from src.graph.state import create_initial_state, Message
from src.graph.workflow import InterviewWorkflow
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


def print_banner():
    """Print the application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║          🤖 AI INTERVIEWER SYSTEM 🤖             ║
    ║                                                   ║
    ║    Multi-Agent Interview Simulation Platform     ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)


def print_agent_header(agent_type: str):
    """Print header when an agent takes over."""
    headers = {
        "technical": f"\n{Fore.BLUE}{'='*50}\n💻 TECHNICAL ROUND\n{'='*50}{Style.RESET_ALL}\n",
        "hr": f"\n{Fore.GREEN}{'='*50}\n🤝 HR ROUND\n{'='*50}{Style.RESET_ALL}\n",
        "manager": f"\n{Fore.MAGENTA}{'='*50}\n👔 MANAGERIAL ROUND\n{'='*50}{Style.RESET_ALL}\n"
    }
    print(headers.get(agent_type, ""))


def print_question(question: str, question_num: int, max_questions: int):
    """Print a question."""
    print(f"\n{Fore.YELLOW}Question {question_num}/{max_questions}:{Style.RESET_ALL}")
    print(f"{question}\n")


def print_completion_message():
    """Print interview completion message."""
    print(f"\n{Fore.GREEN}{'='*50}")
    print("🎉 INTERVIEW COMPLETE!")
    print(f"{'='*50}{Style.RESET_ALL}\n")


def print_info(message: str):
    """Print info message."""
    print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message."""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def print_answer_prompt():
    """Print answer prompt."""
    print(f"{Fore.GREEN}Your answer: {Style.RESET_ALL}", end="")


def format_conversation_summary(qa_pairs):
    """Format conversation summary."""
    if not qa_pairs:
        return "No questions answered."
    
    summary = []
    for i, qa in enumerate(qa_pairs, 1):
        summary.append(f"\nQ{i}: {qa.question}")
        summary.append(f"A{i}: {qa.answer or 'No answer'}\n")
    return "\n".join(summary)


def get_candidate_info() -> tuple[str, str, str]:
    """
    Get candidate information from user input.
    
    Returns:
        tuple: (candidate_name, job_role, experience_level)
    """
    print_banner()
    print_info("Welcome to the AI Interviewer! Let's get started.\n")
    
    candidate_name = input("👤 Please enter your name: ").strip()
    while not candidate_name:
        print_error("Name cannot be empty.")
        candidate_name = input("👤 Please enter your name: ").strip()
    
    job_role = input("💼 Please enter the job role you're applying for: ").strip()
    while not job_role:
        print_error("Job role cannot be empty.")
        job_role = input("💼 Please enter the job role you're applying for: ").strip()
    
    print_info("\nExperience Levels: Junior | Mid-Level | Senior")
    experience_level = input("📊 Please enter your experience level: ").strip()
    while not experience_level:
        print_error("Experience level cannot be empty.")
        experience_level = input("📊 Please enter your experience level: ").strip()
    
    print_info(f"\nGreat! Starting your interview for {experience_level} {job_role} position.\n")
    input("Press Enter to begin...")
    
    return candidate_name, job_role, experience_level



def run_interview():
    """Main function to run the interview."""
    try:
        # Get candidate information
        candidate_name, job_role, experience_level = get_candidate_info()
        
        # Initialize state
        state = create_initial_state(candidate_name, job_role, experience_level)
        
        # Create workflow
        workflow = InterviewWorkflow()
        
        # Track current agent for UI
        current_agent_type = None
        
        # Run interview loop
        while not state["is_complete"]:
            # Check if agent changed
            if state["current_agent"] != current_agent_type:
                current_agent_type = state["current_agent"]
                if current_agent_type != "complete":
                    print_agent_header(current_agent_type)
            
            # Clear last answer before getting new question
            state["last_answer"] = None
            
            # Get next question from workflow
            state = workflow.run_step(state)
            
            # Display the question
            if state["current_question"]:
                agent_type = state["current_agent"]
                
                # Determine question number and max for current agent
                if agent_type == "technical":
                    q_num = state["technical_questions_asked"]
                    max_q = settings.MAX_TECHNICAL_QUESTIONS
                elif agent_type == "hr":
                    q_num = state["hr_questions_asked"]
                    max_q = settings.MAX_HR_QUESTIONS
                else:  # manager
                    q_num = state["manager_questions_asked"]
                    max_q = settings.MAX_MANAGER_QUESTIONS
                
                print_question(state["current_question"], q_num, max_q)
                
                # Get candidate's answer
                print_answer_prompt()
                answer = input().strip()
                
                # Validate answer
                while not answer:
                    print_error("Answer cannot be empty. Please provide an answer.")
                    print_answer_prompt()
                    answer = input().strip()
                
                # Process the answer
                state = workflow.process_answer(state, answer)
                print()  # Add spacing
        
        # Interview completed
        print_completion_message()
        
        # Ask if they want to see summary
        show_summary = input("\nWould you like to see the interview summary? (y/n): ").strip().lower()
        if show_summary == 'y':
            summary = format_conversation_summary(state["qa_pairs"])
            print(summary)
        
        print_info("Thank you for using AI Interviewer!")
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print_info("Interview interrupted by user.")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_interview()