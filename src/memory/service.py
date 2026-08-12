from sqlalchemy import select
from .database import async_session_maker
from .models import Message


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
