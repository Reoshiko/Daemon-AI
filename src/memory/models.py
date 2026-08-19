from sqlalchemy import DateTime, Integer, String, Text, func, Float, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class Base(DeclarativeBase):
    pass


class MemoryType(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    GOAL = "goal"
    EVENT = "event"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


@dataclass
class MemoryContext:
    messages: list[dict[str, str]]
    memories: list[str]


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    type: Mapped[MemoryType] = mapped_column(SQLEnum(MemoryType), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
