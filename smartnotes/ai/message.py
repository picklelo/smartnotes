import datetime
import reflex as rx
from sqlmodel import Column, DateTime, Field, func


class Conversation(rx.Model, table=True):
    name: str

class Message(rx.Model, table=True):
    """A message to send to the agent."""

    role: str
    content: str
    type: str = "text"
    timestamp: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    conversation_id: int | None = Field(default=None, foreign_key="conversation.id")

def UserMessage(**kwargs):
    return Message(role="user", **kwargs)

def SystemMessage(**kwargs):
    return Message(role="system", **kwargs)

def AIMessage(**kwargs):
    return Message(role="assistant", **kwargs)

def ToolMessage(**kwargs):
    return Message(role="tool", **kwargs)

# class UserMessage(Message):
#     """A message from the user."""

#     role = "user"


# class SystemMessage(Message):
#     """A message from the system."""

#     role = "system"


# class AIMessage(Message):
#     """A message from the AI."""

#     role = "assistant"


# class ToolMessage(Message):
#     """A message from a tool."""

#     role = "tool"
