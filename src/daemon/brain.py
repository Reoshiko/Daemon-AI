from src.memory.service import MemoryService
from .llm import LLMClient
from .models import Event, Decision
from .personality import DAEMON_PERSONA
from src.memory.extractor import MemoryExtractor

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
        self.extractor = MemoryExtractor()

    async def process(self, event: Event) -> Decision:
        context = await self.memory.build_context(event.source, limit=10)
        memory_block = ""
        if context.memories:
            memory_block = "\n\nLong-term memories:\n" + "\n".join(
                f"- {memory}" for memory in context.memories
            )
        messages = [
            {
                "role": "system",
                "content": f"{DAEMON_PERSONA}\n\n{RULES}\n\n{memory_block}",
            },
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
        extraction = await self.extractor.extract(
            source=event.source, message=event.content
        )
        for memory in extraction.memories:
            await self.memory.add_memory(
                source=event.source,
                type=memory.type,
                content=memory.content,
                importance=memory.importance,
            )
        return decision
