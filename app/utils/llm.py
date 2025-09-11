from langchain_openai import ChatOpenAI
from app.config.settings import settings

def get_chat_model():
    """Return a reusable chat model with response length constraints"""
    api_key=settings.OPENAI_API_KEY
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY in environment variables")

    return ChatOpenAI(
        api_key=api_key,
        temperature=0,
        model="gpt-3.5-turbo",
        max_tokens=250  
    )
