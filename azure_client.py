"""
Azure OpenAI clients for chat and embeddings.
"""

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from config import settings


def get_chat_llm():
    """
    Create and return a LangChain Azure OpenAI chat client for agents.
    
    Returns:
        AzureChatOpenAI: Configured LLM instance for chat
    """
    return AzureChatOpenAI(
        azure_endpoint=settings.OPENAI_ENDPOINT,
        azure_deployment=settings.OPENAI_DEPLOYMENT_NAME,
        api_version=settings.OPENAI_API_VERSION,
        api_key=settings.OPENAI_API_KEY,
        temperature=settings.TEMPERATURE,
    )


def get_embedding_client():
    """
    Create and return an Azure OpenAI embeddings client configured for LangChain.
    Useful for future RAG/vector search features.
    
    Returns:
        AzureOpenAIEmbeddings: A configured embedding client
    """
    return AzureOpenAIEmbeddings(
        azure_endpoint=settings.OPENAI_ENDPOINT,
        api_key=settings.OPENAI_API_KEY,
        api_version=settings.OPENAI_API_VERSION,
        deployment=settings.OPENAI_EMBED_DEPLOYMENT_NAME,
        model=settings.OPENAI_EMBED_DEPLOYMENT_NAME,
    )
