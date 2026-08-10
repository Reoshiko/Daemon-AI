from .llm import LLMClient
from .models import Event, Decision
from .personality import DAEMON_PERSONA

RULES = """
Ты должен принять решение о реакции на событие
Доступные действия:
reply:
Ты отвечаешь человеку.
message обязательно содержит текст ответа
ignore:
Ты сознательно ничего не отвечаешь
message должен быть null
thought — короткая внутренняя мысль о ситуации
Она используется только внутренней системой и не показывается человеку
"""


class Brain:
    def __init__(self):
        self.llm = LLMClient()

    async def process(self, event: Event) -> Decision:
        messages = [
            {"role": "system", "content": f"{DAEMON_PERSONA}\n\n{RULES}"},
            {
                "role": "user",
                "content": (
                    f"Источник: {event.source}\n",
                    f"Тип события: {event.type}\n",
                    f"Содержание: {event.content}",
                ),
            },
        ]
        return await self.llm.decide(messages)
