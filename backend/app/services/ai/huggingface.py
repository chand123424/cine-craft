from app.services.ai.http_provider import HttpJSONProvider


class HuggingFaceProvider(HttpJSONProvider):
    def __init__(self, api_key: str, model: str = "meta-llama/Llama-3.1-8B-Instruct", **kwargs) -> None:
        super().__init__(api_key, "https://router.huggingface.co/v1/chat/completions", model, **kwargs)
