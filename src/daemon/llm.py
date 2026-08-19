from .models import Decision
from .settings import settings
import httpx
from typing import TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    async def structured(
        self,
        messages: list[dict[str, str]],
        response_model: type[T],
        *,
        temperature: float | None = None,
    ) -> T:

        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            response = await client.post(
                f"{settings.llm_base_url}/v1/chat/completions",
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "temperature": (
                        temperature
                        if temperature is not None
                        else settings.llm_temperature
                    ),
                    "response_format": {
                        "type": "json_object",
                        "schema": response_model.model_json_schema(),
                    },
                },
            )

            if response.is_error:
                raise RuntimeError(f"LLM {response.status_code}: {response.text}")
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return response_model.model_validate_json(content)

    async def decide(self, messages: list[dict[str, str]]) -> Decision:
        return await self.structured(messages, Decision)
