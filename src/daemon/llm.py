from .models import Decision
from .settings import settings
import httpx


class LLMClient:
    async def decide(self, messages: list[str, str]) -> Decision:
        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            response = await client.post(
                f"{settings.llm_base_url}/api/chat",
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "stream": False,
                    "format": Decision.model_json_schema(),
                    "options": {"temperature": settings.llm_temperature},
                },
            )

            response.raise_for_status()
            data = response.json()
            content = data["message"]["content"]
            return Decision.model_validate_json(content)
