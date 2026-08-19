from pydantic import BaseModel, Field
from .models import MemoryType


class ExtractedMemory(BaseModel):
    type: MemoryType
    content: str = Field(min_length=1)
    importance: float = Field(ge=0.0, le=1.0)


class MemoryExtraction(BaseModel):
    memories: list[ExtractedMemory]
