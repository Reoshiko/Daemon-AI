from .llm import LLMClient
from .models import Event, Decision
import json

SYSTEM_PROMPT = """
Для каждого события возвращай только JSON такого формата:
{
  "thought": "твоя внутренняя мысль",
  "action": "reply или ignore",
  "message": "сообщение человеку или null"
}
thought никогда не показывается пользователю.
Если action = ignore, message должен быть null.
"""


class Brain:
    def __init__(self):
        self.llm = LLMClient()

    async def process(self, event: Event) -> Decision:
        prompt = f"""
Источник: {event.source}
Событие: {event.type}
Сообщение: {event.content}
"""
        response = await self.llm.chat(
            [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {"role": "user", "content": prompt},
            ]
        )
        data = json.loads(response)
        return Decision.model_validate(data)
