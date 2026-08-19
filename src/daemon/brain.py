from src.memory.service import MemoryService
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
        self.memory = MemoryService()

    async def process(self, event: Event) -> Decision:
        context = await self.memory.build_context(event.source, limit=10)
        messages = [
            {
                "role": "system",
                "content": f"{DAEMON_PERSONA}\n\n{RULES}"
            },
            *context.messages,
            {
                "role": "user",
                "content": event.content
            }
        ]
        decision = await self.llm.decide(messages)
        await self.memory.store_interaction(
            source=event.source,
            user_message=event.content,
            assistant_message=(decision.message if decision.action == "reply" else None)
        )
        return decision
