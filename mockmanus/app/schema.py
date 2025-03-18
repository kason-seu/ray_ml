from enum import Enum
from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class AgentState(str, Enum):
    """ Agent execution state"""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    NameError = "ERROR"


class Function(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    """Represents a too/ function call in a message"""
    id: str
    type: str = "function"
    function: Function


class Message(BaseModel):
    """Represents a chat message in the conversation"""
    role: Literal["system", "user", "assistant", "tool"] = Field(...)
    content: Optional[str] = Field(default=None)
    tool_calls: Optional[List[ToolCall]] = Field(default=None)
    name: Optional[str] = Field(default=None)
    tool_call_id: Optional[str] = Field(default=None)

    def to_dict(self) -> dict:
        """Convert message to a dictionary format"""
        message = {'role': self.role}
        if self.content is not None:
            message['content'] = self.content
        if self.tool_calls is not None:
            message['tool_calls'] = [tool_call.dict() for tool_call in self.tool_calls]

        if self.name is not None:
            message['name'] = self.name

        if self.tool_call_id is not None:
            message['tool_call_id'] = self.tool_call_id
        return message

    @classmethod
    def user_message(cls, content: str) -> "Message":

        return cls(role="user", content=content)

    @classmethod
    def system_message(cls, content: str) -> "Message":
        return cls(role="system", content=content)


class Memory(BaseModel):
    messages: List[Message] = Field(default_factory=list)
    max_messages: int = Field(default=100)
