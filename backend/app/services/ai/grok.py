from app.services.ai.http_provider import HttpJSONProvider


class GrokProvider(HttpJSONProvider):
    def __init__(self, api_key: str, model: str = "grok-3-mini", **kwargs) -> None:
        super().__init__(api_key, "https://api.x.ai/v1/chat/completions", model, **kwargs)
