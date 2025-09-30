from langchain_openai import ChatOpenAI
from app.config.settings import settings
from app.utils.logging.logger import get_logger


logger = get_logger("LLM")


class FallbackLLM:
    """Dummy LLM that always returns a safe response."""
    def invoke(self, messages, **kwargs):
        return type("LLMResponse", (), {
            "content": (
                "No active language model available. "
                "Please ask about Jorge’s profile, experience, or skills."
            )
        })()


def _get_provider_model(provider: str):
    """
    Try to initialize a provider-specific chat model.
    Returns model instance or None if failed.
    """
    provider = provider.lower()
    try:
        if provider == "openai":
            if not settings.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY missing, skipping provider 'openai'.")
                return None
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                temperature=0,
                max_tokens=250,
            )
        else:
            logger.warning("Unsupported LLM provider configured: %s", provider)
            return None
    except Exception as e:
        logger.error("Failed to initialize provider '%s': %s", provider, e)
        return None


def get_chat_model():
    """
    Return the first available chat model.
    Falls back to FallbackLLM if none available.
    """
    for provider in settings.LLM_PROVIDERS:
        model = _get_provider_model(provider)
        if model:
            logger.info("Using LLM provider: %s", provider)
            return model

    logger.error("No valid LLM provider available. Using fallback.")
    return FallbackLLM()


def get_chat_status() -> dict:
    """
    Returns provider status in a structured format.
    Example: {"status": "online", "provider": "openai"}
    """
    for provider in settings.LLM_PROVIDERS:
        try:
            model = _get_provider_model(provider)
            if not model:
                continue
            model.invoke([{"role": "user", "content": "ping"}])
            return {"status": "online", "provider": provider}
        except Exception as e:
            logger.warning("Provider '%s' ping failed: %s", provider, e)
            continue
    return {"status": "offline", "provider": "fallback"}
