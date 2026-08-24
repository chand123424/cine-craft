from app.services.ai.http_provider import HttpJSONProvider


class GeminiProvider(HttpJSONProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", **kwargs) -> None:
        super().__init__(api_key, "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", model, **kwargs)
