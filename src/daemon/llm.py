import httpx


class LLMClient:
    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "qwen3:4b"
    ):
        self.base_url = base_url
        self.model = model

    async def chat(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
            )

            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
