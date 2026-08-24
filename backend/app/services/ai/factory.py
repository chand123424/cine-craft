from app.config import Settings
from app.exceptions import AIProviderError
from app.services.ai.base import AIProvider
from app.services.ai.gemini import GeminiProvider
from app.services.ai.grok import GrokProvider
from app.services.ai.huggingface import HuggingFaceProvider
from app.services.ai.mock import MockProvider


def get_provider(settings: Settings) -> AIProvider:
    common = {"timeout": settings.request_timeout_seconds, "retries": settings.ai_max_retries}
    if settings.ai_provider == "mock":
        return MockProvider()
    if settings.ai_provider == "gemini" and settings.google_ai_api_key:
        return GeminiProvider(settings.google_ai_api_key, settings.ai_model or "gemini-2.0-flash", **common)
    if settings.ai_provider == "grok" and settings.grok_api_key:
        return GrokProvider(settings.grok_api_key, settings.ai_model or "grok-3-mini", **common)
    if settings.ai_provider == "huggingface" and settings.huggingface_api_key:
        return HuggingFaceProvider(settings.huggingface_api_key, settings.ai_model or "meta-llama/Llama-3.1-8B-Instruct", **common)
    raise AIProviderError(f"AI provider '{settings.ai_provider}' is not configured")
