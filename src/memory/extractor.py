from src.daemon.llm import LLMClient
from .schemas import MemoryExtraction

EXTRACTION_PROMPT = """
Extract useful long-term memories from the user's message.
Store only information that could reasonably matter in future conversations.
Memory types:
fact:
Stable information about the user or their world.
preference:
Something the user likes, dislikes, prefers, enjoys, or avoids.
goal:
Something the user wants to achieve, build, learn, or do.
event:
A meaningful thing that happened to the user.
Rules:
- Do not store greetings or casual filler.
- Do not invent information.
- Memories must make sense without the original conversation.
- Rewrite first-person statements so the subject is explicit.
- Usually extract 0-3 memories.
- importance must be between 0 and 1.
"""


class MemoryExtractor:
    def __init__(self):
        self.llm = LLMClient()

    async def extract(self, *, source: str, message: str) -> MemoryExtraction:
        return await self.llm.structured(
            [
                {"role": "system", "content": EXTRACTION_PROMPT},
                {
                    "role": "user",
                    "content": (f"User/source: {source}\n" f"Message: {message}"),
                },
            ],
            MemoryExtraction,
            temperature=0.2,
        )
