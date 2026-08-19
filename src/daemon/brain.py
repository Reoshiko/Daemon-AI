from src.memory.service import MemoryService
from .llm import LLMClient
from .models import Event, Decision
from .personality import DAEMON_PERSONA

RULES = """
Return only JSON.
Rules:
- action = "reply":
  message must be a non-empty response to the user.
- action = "ignore":
  message must be null.
  Use ignore only when there is a real reason not to respond.
- thought:
  short private internal thought.
  It must not be empty.
Language:
- Reply in the same language as the user.
- If the user writes in English, reply in English.
- If the user writes in Russian, reply in Russian.
No markdown.
No explanations outside JSON.
"""


class Brain:
    def __init__(self):
        self.llm = LLMClient()
        self.memory = MemoryService()

    async def process(self, event: Event) -> Decision:
        context = await self.memory.build_context(event.source, limit=10)
        messages = [
            {"role": "system", "content": f"{DAEMON_PERSONA}\n\n{RULES}"},
            *context.messages,
            {"role": "user", "content": event.content},
        ]
        decision = await self.llm.decide(messages)
        await self.memory.store_interaction(
            source=event.source,
            user_message=event.content,
            assistant_message=(
                decision.message if decision.action == "reply" else None
            ),
        )
        return decision
