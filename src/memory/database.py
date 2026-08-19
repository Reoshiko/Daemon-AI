from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

engine = create_async_engine("sqlite+aiosqlite:///./daemon.db")

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables() -> None:
    from .models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
                USING fts5(
                    content,
                    content='memories',
                    content_rowid='id'
                )
                """))

        await conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS memories_ai
                AFTER INSERT ON memories
                BEGIN
                    INSERT INTO memories_fts(rowid, content)
                    VALUES (new.id, new.content);
                END
                """))

        await conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS memories_ad
                AFTER DELETE ON memories
                BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, content)
                    VALUES ('delete', old.id, old.content);
                END
                """))

        await conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS memories_au
                AFTER UPDATE ON memories
                BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, content)
                    VALUES ('delete', old.id, old.content);

                    INSERT INTO memories_fts(rowid, content)
                    VALUES (new.id, new.content);
                END
                """))
