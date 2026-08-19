from sqlalchemy import select
from .database import async_session_maker
from .models import Message, MemoryContext


class MemoryService:
    async def add_message(self, *, source: str, role: str, content: str) -> None:
        async with async_session_maker() as session:
            session.add(Message(source=source, role=role, content=content))
            await session.commit()

    async def get_recent_messages(self, source: str, limit: int = 10) -> list[Message]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(Message)
                .where(Message.source == source)
                .order_by(Message.id.desc())
                .limit(limit)
            )
            messages = list(result.scalars())

        messages.reverse()

        return messages

    async def build_context(self, source: str, limit: int = 10) -> MemoryContext:
        history = await self.get_recent_messages(source=source, limit=limit)
        return MemoryContext(
            messages=[{"role": item.role, "content": item.content} for item in history]
        )

    async def store_interaction(
        self, *, source: str, user_message: str, assistant_message: str | None
    ) -> None:
        await self.add_message(source=source, role="assistant", content=user_message)

        if assistant_message:
            await self.add_message(
                source=source, role="assistant", content=assistant_message
            )
