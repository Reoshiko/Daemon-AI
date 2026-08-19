from .models import Decision
from .settings import settings
import httpx


class LLMClient:
    async def decide(self, messages: list[dict[str, str]]) -> Decision:
        schema = Decision.model_json_schema()

        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            response = await client.post(
                f"{settings.llm_base_url}/v1/chat/completions",
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "temperature": settings.llm_temperature,
                    "response_format": {
                        "type": "json_object",
                        "schema": schema
                    }
                },
            )

            if response.is_error:
                raise RuntimeError(f"LLM {response.status_code}: {response.text}")
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return Decision.model_validate_json(content)
