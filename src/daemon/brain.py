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
        history = await self.memory.get_recent_messages(event.source, limit=10)
        messages = [
            {"role": "system", "content": f"{DAEMON_PERSONA}\n\n{RULES}"},
        ]
        for item in history:
            messages.append({"role": item.role, "content": item.content})
        messages.append({"role": "user", "content": event.content})

        decision = await self.llm.decide(messages)
        await self.memory.add_message(
            source=event.source, role="user", content=event.content
        )

        if decision.action == "reply":
            await self.memory.add_message(
                source=event.source, role="assistant", content=decision.message
            )

        return decision
