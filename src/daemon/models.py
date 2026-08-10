from pydantic import BaseModel, model_validator
from typing import Literal


class Event(BaseModel):
    type: Literal["message"]
    source: str
    content: str


class Decision(BaseModel):
    thought: str
    action: Literal["reply", "ignore"]
    message: str | None = None

    @classmethod
    @model_validator(mode="after")
    def validate_action(self):
        if self.action == "reply" and not self.message:
            raise ValueError("reply requires message")
        if self.action == "ignore":
            self.message = None
        return self
