from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings


def _get_provider_model(provider: str):
    """Return a chat model instance for the given provider name."""
    provider = provider.lower()

    if provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("Missing OPENAI_API_KEY")
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0,
            max_tokens=250,
        )

    elif provider == "openrouter":
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("Missing OPENROUTER_API_KEY")
        return ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            model="x-ai/grok-4-fast:free",
            base_url="https://openrouter.ai/api/v1",
            temperature=0,
            max_tokens=250,
        )

    elif provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("Missing GEMINI_API_KEY")
        return ChatGoogleGenerativeAI(
            api_key=settings.GEMINI_API_KEY,
            model="gemini-2.5-flash",
            temperature=0,
            max_output_tokens=250,  
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def get_chat_model():
    """
    Return a reusable chat model.
    Tries providers in order defined in settings.LLM_PROVIDERS until one works.
    """
    last_error = None

    for provider in settings.LLM_PROVIDERS:
        try:
            return _get_provider_model(provider)
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")


def get_chat_status() -> dict:
    """
    Returns provider status in a structured format.
    Example: {"status": "online", "provider": "openai"}
    """
    for provider in settings.LLM_PROVIDERS:
        try:
            model = _get_provider_model(provider)
            model.invoke([{"role": "user", "content": "ping"}])
            return {"status": "online", "provider": provider}
        except Exception:
            continue

    return {"status": "offline", "provider": None}