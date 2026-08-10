from pydantic import BaseModel
from typing import Literal


class Event(BaseModel):
    type: Literal["message"]
    source: str
    content: str


class Decision(BaseModel):
    thought: str
    action: Literal["reply", "ignore"]
    message: str | None = None
