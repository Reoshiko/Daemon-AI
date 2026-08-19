from pydantic import BaseModel, model_validator, Field
from typing import Literal


class Event(BaseModel):
    type: Literal["message"]
    source: str
    content: str


class Decision(BaseModel):
    thought: str = Field(min_length=1)
    action: Literal["reply", "ignore"]
    message: str | None = None

    @classmethod
    @model_validator(mode="after")
    def validate_action(self):
        if self.action == "reply":
            if not self.message or not self.message.strip():
                raise ValueError("reply requires non-empty message")
        if self.action == "ignore":
            self.message = None
        return self