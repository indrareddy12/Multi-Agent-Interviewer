"""
Streamlit Frontend for AI Interviewer
A professional interview simulation platform with multi-agent orchestration.
"""

import streamlit as st
import sys
import os
from datetime import datetime
import io

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Load Streamlit secrets to environment variables (for cloud deployment)
if hasattr(st, 'secrets'):
    try:
        for key, value in st.secrets.items():
            if key not in os.environ:
                os.environ[key] = str(value)
    except Exception as e:
        st.warning(f"Could not load secrets: {e}")

# Setup logging before importing other modules
from config.logging_config import setup_logging, get_logger
setup_logging(log_to_file=True)
logger = get_logger(__name__)

from src.graph.state import create_initial_state, Message, QuestionAnswer
from src.graph.workflow import InterviewWorkflow

# Document processing imports
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger.warning("PyPDF2 not installed - PDF resume upload disabled")

try:
    import docx
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False
    logger.warning("python-docx not installed - DOCX resume upload disabled")

logger.info("="*60)
logger.info("AI Interviewer Streamlit Application Started")
logger.info("="*60)


# Page configuration
st.set_page_config(
    page_title="AI Interviewer Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    /* Light, clean background */
    .stApp {
        background: linear-gradient(135deg, #e0f2fe 0%, #ddd6fe 50%, #fce7f3 100%);
        background-attachment: fixed;
    }
    
    /* Content area - pure white */
    .main .block-container {
        background: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #3b82f6 0%, #8b5cf6 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        color: #1e293b;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }
    
    .sub-header {
        text-align: center;
        color: #475569;
        margin-bottom: 2rem;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    .agent-card {
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    .technical-card {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        color: white;
    }
    
    .hr-card {
        background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
        color: white;
    }
    
    .manager-card {
        background: linear-gradient(135deg, #06b6d4 0%, #14b8a6 100%);
        color: white;
    }
    
    .question-box {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin: 1rem 0;
        color: #1e293b;
        font-size: 1.1rem;
        line-height: 1.8;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .score-card {
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    .excellent-score {
        background: linear-gradient(135deg, #10b981 0%, #22c55e 100%);
        color: white;
    }
    
    .good-score {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        color: white;
    }
    
    .average-score {
        background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
        color: white;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
    }
    
    /* Form elements - clean white with dark text */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        background-color: #fefce8 !important;
        color: #0f172a !important;
        font-size: 1rem;
        padding: 0.75rem;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    /* Selectbox - WHITE background with dark text */
    .stSelectbox [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div:hover {
        border-color: #3b82f6 !important;
    }
    
    .stSelectbox [data-baseweb="select"] input {
        color: #0f172a !important;
    }
    
    .stSelectbox [data-baseweb="select"] span {
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    
    /* Dropdown menu when opened */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    
    [role="listbox"] {
        background-color: #ffffff !important;
    }
    
    [role="option"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    
    [role="option"]:hover {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        outline: none;
    }
    
    /* Dropdown arrow area */
    .stSelectbox svg {
        color: #3b82f6 !important;
    }
    
    /* Labels - dark and clear */
    label {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Text elements - dark for readability */
    .stMarkdown {
        color: #1e293b;
    }
    
    p, span, div {
        color: #334155;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    
    /* Radio buttons - clear labels */
    .stRadio > label {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stRadio > div {
        color: #1e293b !important;
    }
    
    .stRadio > div > label {
        color: #334155 !important;
        font-weight: 500 !important;
    }
    
    /* Buttons - vibrant and clear */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.05rem;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
    }
    
    /* File uploader - light background */
    [data-testid="stFileUploader"] {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px dashed #cbd5e0;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background: #f1f5f9;
    }
    
    [data-testid="stFileUploader"] label {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #f0fdf4 !important;
        color: #166534 !important;
        padding: 1rem;
        border-radius: 8px;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        color: #991b1b !important;
        padding: 1rem;
        border-radius: 8px;
    }
    
    /* Expander - clean styling */
    .streamlit-expanderHeader {
        background-color: #f8fafc !important;
        color: #1e293b !important;
        border-radius: 8px;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.75rem;
            padding: 0.5rem 0;
        }
        
        .sub-header {
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }
        
        .main .block-container {
            padding: 1.25rem;
        }
        
        .agent-card {
            padding: 1.25rem;
        }
        
        .question-box {
            font-size: 1rem;
            padding: 1.25rem;
            line-height: 1.6;
        }
        
        label {
            font-size: 0.95rem !important;
        }
        
        .stButton > button {
            font-size: 1rem;
            padding: 0.65rem 1.5rem;
            width: 100%;
        }
        
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            font-size: 16px; /* Prevents zoom on iOS */
        }
    }
    
    /* Tablet responsiveness */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main-header {
            font-size: 2.25rem;
        }
        
        .main .block-container {
            padding: 1.75rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# Job roles and experience levels
JOB_ROLES = [
    "Software Engineer",
    "Data Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Product Manager",
    "System Architect",
    "PowerBI Analyst",
    "Google Looker Analyst",
    "Business Intelligence Analyst",
    "Other (Specify)"
]

EXPERIENCE_LEVELS = ["Junior", "Mid-Level", "Senior"]


def extract_text_from_pdf(file):
    """Extract text from PDF file."""
    if not PDF_SUPPORT:
        return None
    
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        logger.info(f"Successfully extracted {len(text)} characters from PDF resume")
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return None


def extract_text_from_docx(file):
    """Extract text from DOCX file."""
    if not DOCX_SUPPORT:
        return None
    
    try:
        doc = docx.Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        logger.info(f"Successfully extracted {len(text)} characters from DOCX resume")
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting DOCX text: {e}")
        return None


def extract_text_from_txt(file):
    """Extract text from TXT file."""
    try:
        text = file.read().decode('utf-8')
        logger.info(f"Successfully extracted {len(text)} characters from TXT resume")
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting TXT text: {e}")
        return None


def process_resume_upload(uploaded_file):
    """Process uploaded resume file and extract text."""
    if uploaded_file is None:
        return None
    
    file_type = uploaded_file.name.split('.')[-1].lower()
    logger.info(f"Processing resume upload: {uploaded_file.name} (type: {file_type})")
    
    if file_type == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_type in ['docx', 'doc']:
        return extract_text_from_docx(uploaded_file)
    elif file_type == 'txt':
        return extract_text_from_txt(uploaded_file)
    else:
        logger.warning(f"Unsupported file type: {file_type}")
        return None


def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'stage' not in st.session_state:
        st.session_state.stage = 'welcome'
    if 'candidate_name' not in st.session_state:
        st.session_state.candidate_name = ''
    if 'job_role' not in st.session_state:
        st.session_state.job_role = ''
    if 'experience_level' not in st.session_state:
        st.session_state.experience_level = ''
    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = None
    if 'workflow' not in st.session_state:
        st.session_state.workflow = None
    if 'current_answer' not in st.session_state:
        st.session_state.current_answer = ''
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = None


def show_welcome_screen():
    """Display the welcome screen."""
    st.markdown('<h1 class="main-header">🤖 AI Interviewer Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Experience a realistic interview simulation powered by AI</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Welcome! 👋")
        st.write("This platform simulates a complete interview process with three specialized AI agents:")
        
        st.markdown("""
        <div class="agent-card technical-card">
            <h4>💻 Technical Interviewer</h4>
            <p>Assesses your coding skills, system design knowledge, and problem-solving abilities</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card hr-card">
            <h4>🤝 HR Manager</h4>
            <p>Evaluates cultural fit, soft skills, and communication abilities</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card manager-card">
            <h4>👔 Hiring Manager</h4>
            <p>Assesses leadership potential, strategic thinking, and career vision</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Candidate Information Form
        st.markdown("### Let's Get Started")
        
        candidate_name = st.text_input(
            "👤 Your Name",
            placeholder="Enter your full name",
            key="name_input"
        )
        
        # Job Role Selection
        col_role1, col_role2 = st.columns([3, 1])
        with col_role1:
            job_role_selection = st.selectbox(
                "💼 Job Role",
                JOB_ROLES,
                key="role_select"
            )
        
        if job_role_selection == "Other (Specify)":
            custom_role = st.text_input(
                "Specify your role",
                placeholder="e.g., Cloud Architect",
                key="custom_role"
            )
            job_role = custom_role if custom_role else ""
        else:
            job_role = job_role_selection
        
        # Experience Level
        experience_level = st.radio(
            "📊 Experience Level",
            EXPERIENCE_LEVELS,
            horizontal=True,
            key="exp_level"
        )
        
        # Resume Upload Section
        st.markdown("#### 📄 Resume Upload (Optional)")
        st.markdown("Upload your resume to help the AI ask more personalized questions based on your experience.")
        
        supported_formats = []
        if PDF_SUPPORT:
            supported_formats.append("pdf")
        if DOCX_SUPPORT:
            supported_formats.extend(["docx", "doc"])
        supported_formats.append("txt")
        
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=supported_formats,
            help=f"Supported formats: {', '.join(supported_formats).upper()}",
            key="resume_upload"
        )
        
        resume_text = None
        if uploaded_file is not None:
            with st.spinner("Processing your resume..."):
                resume_text = process_resume_upload(uploaded_file)
                if resume_text:
                    st.success(f"✅ Resume processed successfully! ({len(resume_text)} characters extracted)")
                    with st.expander("📝 Preview extracted text"):
                        st.text_area("Resume Content", resume_text[:1000] + ("..." if len(resume_text) > 1000 else ""), height=200, disabled=True)
                else:
                    st.error("❌ Failed to process resume. Please try a different file or continue without it.")
        
        st.markdown("---")
        
        # Start Button
        if st.button("🚀 Start Interview", type="primary", use_container_width=True):
            if candidate_name and job_role:
                resume_status = "with resume" if resume_text else "without resume"
                logger.info(f"Starting new interview - Candidate: {candidate_name}, Role: {job_role}, Level: {experience_level}, {resume_status}")
                
                st.session_state.candidate_name = candidate_name
                st.session_state.job_role = job_role
                st.session_state.experience_level = experience_level
                st.session_state.resume_text = resume_text
                st.session_state.stage = 'interview'
                st.session_state.interview_started = True
                
                # Initialize interview state and workflow
                st.session_state.interview_state = create_initial_state(
                    candidate_name=candidate_name,
                    job_role=job_role,
                    experience_level=experience_level,
                    resume_text=resume_text
                )
                st.session_state.workflow = InterviewWorkflow()
                logger.info("Interview state and workflow initialized")
                
                st.rerun()
            else:
                st.error("Please fill in all required fields!")


def get_agent_header(agent_type):
    """Get the header for each agent type."""
    headers = {
        "technical": {
            "emoji": "💻",
            "title": "Technical Round",
            "color": "technical-card",
            "description": "Testing your technical skills and problem-solving abilities"
        },
        "hr": {
            "emoji": "🤝",
            "title": "HR Round",
            "color": "hr-card",
            "description": "Evaluating cultural fit and soft skills"
        },
        "manager": {
            "emoji": "👔",
            "title": "Managerial Round",
            "color": "manager-card",
            "description": "Assessing leadership and strategic thinking"
        }
    }
    return headers.get(agent_type, headers["technical"])


def show_interview_screen():
    """Display the interview screen."""
    state = st.session_state.interview_state
    workflow = st.session_state.workflow
    
    # Sidebar with progress
    with st.sidebar:
        st.markdown("### 📋 Interview Progress")
        st.markdown(f"**Candidate:** {state['candidate_name']}")
        st.markdown(f"**Role:** {state['experience_level']} {state['job_role']}")
        st.markdown("---")
        
        # Progress tracking
        from config import settings
        total_questions = (
            settings.MAX_TECHNICAL_QUESTIONS + 
            settings.MAX_HR_QUESTIONS + 
            settings.MAX_MANAGER_QUESTIONS
        )
        current_questions = (
            state['technical_questions_asked'] + 
            state['hr_questions_asked'] + 
            state['manager_questions_asked']
        )
        
        # Cap progress between 0.0 and 1.0
        progress = min(1.0, max(0.0, current_questions / total_questions))
        st.progress(progress)
        st.markdown(f"**Questions: {current_questions}/{total_questions}**")
        
        st.markdown("---")
        st.markdown("**Rounds Completed:**")
        
        tech_progress = f"{state['technical_questions_asked']}/{settings.MAX_TECHNICAL_QUESTIONS}"
        hr_progress = f"{state['hr_questions_asked']}/{settings.MAX_HR_QUESTIONS}"
        mgr_progress = f"{state['manager_questions_asked']}/{settings.MAX_MANAGER_QUESTIONS}"
        
        st.markdown(f"✅ Technical: {tech_progress}")
        st.markdown(f"{'✅' if state['hr_questions_asked'] > 0 else '⏳'} HR: {hr_progress}")
        st.markdown(f"{'✅' if state['manager_questions_asked'] > 0 else '⏳'} Manager: {mgr_progress}")
    
    # Main interview area
    if not state['is_complete']:
        # Get current question if not already set
        if not state.get('current_question'):
            state = workflow.run_step(state)
            st.session_state.interview_state = state
            st.rerun()
        
        current_agent = state['current_agent']
        agent_info = get_agent_header(current_agent)
        
        # Agent Header
        st.markdown(f"""
        <div class="agent-card {agent_info['color']}">
            <h2>{agent_info['emoji']} {agent_info['title']}</h2>
            <p>{agent_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Question number
        if current_agent == "technical":
            q_num = state['technical_questions_asked'] + 1
            max_q = settings.MAX_TECHNICAL_QUESTIONS
        elif current_agent == "hr":
            q_num = state['hr_questions_asked'] + 1
            max_q = settings.MAX_HR_QUESTIONS
        else:
            q_num = state['manager_questions_asked'] + 1
            max_q = settings.MAX_MANAGER_QUESTIONS
        
        st.markdown(f"### Question {q_num}/{max_q}")
        
        # Display question
        st.markdown(f"""
        <div class="question-box">
            {state['current_question']}
        </div>
        """, unsafe_allow_html=True)
        
        # Answer input
        answer = st.text_area(
            "Your Answer:",
            height=150,
            placeholder="Type your answer here...",
            key=f"answer_{current_agent}_{q_num}"
        )
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submit_clicked = st.button(
                "Submit Answer", 
                type="primary", 
                use_container_width=True,
                key=f"submit_{current_agent}_{q_num}"
            )
            
        if submit_clicked:
            if answer.strip():
                logger.info(f"Answer submitted for {current_agent} - Question {q_num} (length: {len(answer)} chars)")
                with st.spinner("Processing your answer..."):
                    # Process the answer
                    state = workflow.process_answer(state, answer)
                    st.session_state.interview_state = state
                    
                    # Check if we've completed all questions before generating next one
                    from config import settings
                    if (state['technical_questions_asked'] >= settings.MAX_TECHNICAL_QUESTIONS and
                        state['hr_questions_asked'] >= settings.MAX_HR_QUESTIONS and
                        state['manager_questions_asked'] >= settings.MAX_MANAGER_QUESTIONS):
                        # Trigger evaluation node
                        logger.info("All questions completed - triggering AI evaluation")
                        with st.spinner("🤖 AI is evaluating your interview performance..."):
                            state = workflow.run_step(state)
                            st.session_state.interview_state = state
                        logger.info("Interview evaluation completed successfully")
                        st.success("🎉 Interview Complete! Your results are ready!")
                    else:
                        # Run the next step to generate the next question
                        logger.debug(f"Generating next question - Current state: Tech={state['technical_questions_asked']}, HR={state['hr_questions_asked']}, Manager={state['manager_questions_asked']}")
                        state = workflow.run_step(state)
                        st.session_state.interview_state = state
                        
                st.rerun()
            else:
                logger.warning("Empty answer submission attempt")
                st.error("Please provide an answer before submitting!")
    
    else:
        # Interview complete - show results
        show_results_screen()


def calculate_interview_score(qa_pairs):
    """
    Calculate interview score based on answer quality.
    This is a simple simulation - you can make it more sophisticated.
    """
    if not qa_pairs:
        return 0
    
    # Simple scoring based on answer length and presence
    total_score = 0
    for qa in qa_pairs:
        answer_length = len(qa.answer or '')
        # Score based on answer length (capped at 100)
        score = min(100, (answer_length / 10) * 10)
        total_score += score
    
    return int(total_score / len(qa_pairs))


def generate_feedback(qa_pairs, score):
    """Generate feedback based on the interview."""
    feedback = {
        "strengths": [],
        "weaknesses": [],
        "suggestions": []
    }
    
    # Analyze by agent type
    technical_answers = [qa for qa in qa_pairs if qa.agent_type == 'technical']
    hr_answers = [qa for qa in qa_pairs if qa.agent_type == 'hr']
    manager_answers = [qa for qa in qa_pairs if qa.agent_type == 'manager']
    
    # Technical feedback
    if technical_answers:
        avg_length = sum(len(qa.answer or '') for qa in technical_answers) / len(technical_answers)
        if avg_length > 200:
            feedback["strengths"].append("Provided detailed technical explanations")
        else:
            feedback["weaknesses"].append("Technical answers could be more detailed")
    
    # HR feedback
    if hr_answers:
        avg_length = sum(len(qa.answer or '') for qa in hr_answers) / len(hr_answers)
        if avg_length > 150:
            feedback["strengths"].append("Demonstrated good communication skills")
        else:
            feedback["suggestions"].append("Try to elaborate more on soft skills and experiences")
    
    # Manager feedback
    if manager_answers:
        avg_length = sum(len(qa.answer or '') for qa in manager_answers) / len(manager_answers)
        if avg_length > 150:
            feedback["strengths"].append("Showed strategic thinking and vision")
        else:
            feedback["suggestions"].append("Develop more comprehensive answers for leadership questions")
    
    # Overall feedback based on score
    if score >= 80:
        feedback["strengths"].append("Excellent overall performance")
    elif score >= 60:
        feedback["suggestions"].append("Good performance, room for improvement in depth")
    else:
        feedback["suggestions"].append("Practice providing more comprehensive answers")
    
    return feedback


def show_results_screen():
    """Display the results screen with scores and feedback."""
    state = st.session_state.interview_state
    
    st.markdown('<h1 class="main-header">🎉 Interview Complete!</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Thank you, {state["candidate_name"]}!</p>', unsafe_allow_html=True)
    
    # Check if AI evaluation is available
    if state.get('evaluation'):
        # Use AI-generated evaluation
        evaluation = state['evaluation']
        score = evaluation.get('score', 0)
        
        # Score card
        score_class = "excellent-score" if score >= 80 else "good-score" if score >= 60 else "average-score"
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div class="score-card {score_class}">
                <h1 style="font-size: 4rem; margin: 0;">{score}</h1>
                <h3>Overall Score</h3>
                <p>out of 100</p>
            </div>
            """, unsafe_allow_html=True)
        
        # AI-Generated Feedback
        st.markdown("---")
        
        # Overall Feedback
        if evaluation.get('overall_feedback'):
            st.markdown("### 📝 Overall Feedback")
            st.info(evaluation['overall_feedback'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💪 Strengths")
            if evaluation.get("strengths"):
                for strength in evaluation["strengths"]:
                    st.success(f"✓ {strength}")
            else:
                st.info("Keep working on building your strengths!")
            
            st.markdown("### 🎯 Suggestions")
            if evaluation.get("suggestions"):
                for suggestion in evaluation["suggestions"]:
                    st.info(f"💡 {suggestion}")
            else:
                st.success("Great job! Keep up the good work!")
        
        with col2:
            st.markdown("### 🔧 Areas for Improvement")
            if evaluation.get("weaknesses"):
                for weakness in evaluation["weaknesses"]:
                    st.warning(f"⚠️ {weakness}")
            else:
                st.success("Excellent performance across the board!")
    else:
        # Fallback to simple calculation if evaluation not available
        score = calculate_interview_score(state['qa_pairs'])
        feedback = generate_feedback(state['qa_pairs'], score)
        
        # Score card
        score_class = "excellent-score" if score >= 80 else "good-score" if score >= 60 else "average-score"
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div class="score-card {score_class}">
                <h1 style="font-size: 4rem; margin: 0;">{score}</h1>
                <h3>Overall Score</h3>
                <p>out of 100</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Feedback
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💪 Strengths")
            if feedback["strengths"]:
                for strength in feedback["strengths"]:
                    st.success(f"✓ {strength}")
            else:
                st.info("Keep practicing to develop your strengths!")
        
        with col2:
            st.markdown("### 📈 Areas for Improvement")
            if feedback["weaknesses"]:
                for weakness in feedback["weaknesses"]:
                    st.warning(f"○ {weakness}")
            if feedback["suggestions"]:
                for suggestion in feedback["suggestions"]:
                    st.info(f"💡 {suggestion}")
    
    st.markdown("---")
    
    # Interview Summary
    with st.expander("📋 View Complete Interview Transcript"):
        current_agent_type = None
        
        for i, qa in enumerate(state['qa_pairs'], 1):
            # Show agent header when it changes
            if qa.agent_type != current_agent_type:
                current_agent_type = qa.agent_type
                agent_info = get_agent_header(current_agent_type)
                st.markdown(f"### {agent_info['emoji']} {agent_info['title']}")
            
            st.markdown(f"**Q{i}:** {qa.question}")
            st.markdown(f"**A:** {qa.answer or ''}")
            st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Start New Interview", type="primary", use_container_width=True):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def main():
    """Main application entry point."""
    initialize_session_state()
    
    if st.session_state.stage == 'welcome':
        show_welcome_screen()
    elif st.session_state.stage == 'interview':
        show_interview_screen()


if __name__ == "__main__":
    main()