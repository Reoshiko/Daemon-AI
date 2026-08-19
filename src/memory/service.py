from sqlalchemy import select, text
from .database import async_session_maker
from .models import Message, MemoryContext, Memory, MemoryType, RetrievedMemory


class MemoryService:
    async def add_message(
        self,
        *,
        source: str,
        role: str,
        content: str,
    ) -> None:
        async with async_session_maker() as session:
            session.add(
                Message(
                    source=source,
                    role=role,
                    content=content,
                )
            )
            await session.commit()

    async def add_memory(
        self,
        *,
        source: str,
        type: MemoryType,
        content: str,
        importance: float,
    ) -> None:
        async with async_session_maker() as session:
            session.add(
                Memory(source=source, type=type, content=content, importance=importance)
            )
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

    async def build_context(
        self, source: str, query: str, limit: int = 10
    ) -> MemoryContext:
        history = await self.get_recent_messages(source=source, limit=limit)
        memories = await self.search_memories(source=source, query=query, limit=limit)
        return MemoryContext(
            messages=[{"role": item.role, "content": item.content} for item in history],
            memories=[item.content for item in memories],
        )

    async def store_interaction(
        self, *, source: str, user_message: str, assistant_message: str | None
    ) -> None:
        await self.add_message(source=source, role="user", content=user_message)

        if assistant_message:
            await self.add_message(
                source=source, role="assistant", content=assistant_message
            )

    async def get_memories(self, source: str, limit: int = 10) -> list[Memory]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(Memory)
                .where(Memory.source == source)
                .order_by(Memory.importance.desc(), Memory.id.desc())
                .limit(limit)
            )
            return list(result.scalars())

    async def search_memories(
        self, source: str, query: str, limit: int = 10
    ) -> list[RetrievedMemory]:
        async with async_session_maker() as session:
            result = await session.execute(
                text("""
                SELECT m.*
                FROM memories_fts f
                JOIN memories m ON m.id = f.rowid
                WHERE memories_fts MATCH :query
                  AND m.source = :source
                ORDER BY bm25(memories_fts)
                LIMIT :limit
                """),
                {
                    "query": query,
                    "source": source,
                    "limit": limit,
                },
            )
            rows = result.mappings().all()
            return [
                RetrievedMemory(
                    id=row.id,
                    type=MemoryType(row.type),
                    content=row.content,
                    importance=row.importance,
                )
                for row in rows
            ]
