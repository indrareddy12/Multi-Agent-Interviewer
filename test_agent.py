"""
Quick test script for the agent's generate_question function.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.agents.technical_agent import TechnicalAgent
from src.graph.state import create_initial_state


def test_generate_question():
    """Test the technical agent's question generation."""
    print("=" * 60)
    print("Testing Technical Agent - Generate Question")
    print("=" * 60)
    
    # Create a technical agent
    print("\n1. Initializing Technical Agent...")
    agent = TechnicalAgent()
    print("   ✓ Agent initialized successfully")
    
    # Create a mock interview state
    print("\n2. Creating interview state...")
    state = create_initial_state(
        candidate_name="John Doe",
        job_role="GenAI Engineer",
        experience_level="Junior"
    )
    print(f"   ✓ State created for: {state['candidate_name']}")
    print(f"   ✓ Job role: {state['job_role']}")
    print(f"   ✓ Experience level: {state['experience_level']}")
    
    # Generate a question
    print("\n3. Generating first technical question...")
    print("   (This may take a few seconds...)")
    try:
        question = agent.ask_question(state)
        print("\n" + "=" * 60)
        print("GENERATED QUESTION:")
        print("=" * 60)
        print(question)
        print("=" * 60)
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error generating question: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_generate_question()