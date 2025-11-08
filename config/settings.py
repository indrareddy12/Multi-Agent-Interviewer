"""
Configuration settings for the AI Interviewer application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Azure OpenAI Configuration
# These can be set in .env file locally or as Streamlit secrets in cloud
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT") 
OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_CHAT_DEPLOYMENT_NAME") 
OPENAI_EMBED_DEPLOYMENT_NAME = os.getenv("OPENAI_EMBED_DEPLOYMENT_NAME") 
OPENAI_API_VERSION = os.getenv("API_VERSION") 

# Validate required settings
if not OPENAI_API_KEY:
    raise ValueError(
        "Missing Azure OpenAI API Key. Please set OPENAI_API_KEY  "
        "environment variable or configure it in Streamlit secrets."
    )

if not OPENAI_ENDPOINT:
    raise ValueError(
        "Missing Azure OpenAI Endpoint. Please set OPENAI_ENDPOINT  "
        "environment variable or configure it in Streamlit secrets."
    )

if not OPENAI_DEPLOYMENT_NAME:
    raise ValueError(
        "Missing Azure OpenAI Chat Deployment Name. Please set OPENAI_CHAT_DEPLOYMENT_NAME or "
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME environment variable or configure it in Streamlit secrets."
    )

# Interview Configuration
MAX_TECHNICAL_QUESTIONS = int(os.getenv("MAX_TECHNICAL_QUESTIONS", "6"))
MAX_HR_QUESTIONS = int(os.getenv("MAX_HR_QUESTIONS", "3"))
MAX_MANAGER_QUESTIONS = int(os.getenv("MAX_MANAGER_QUESTIONS", "2"))

# Model Configuration
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
