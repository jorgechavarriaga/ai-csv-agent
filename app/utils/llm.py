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


def get_chat_status() -> str:
    """Returns 'online' if ChatOpenAI is available and responsive."""
    api_key=settings.OPENAI_API_KEY
    try:
        model = ChatOpenAI(
            api_key=api_key,
            model="gpt-3.5-turbo",
            max_tokens=1,
            temperature=0,
        )
        model.invoke([{"role": "user", "content": "ping"}])
        return "online"
    except Exception as e:
        if "insufficient_quota" in str(e):
            return "offline"
        return "offline"