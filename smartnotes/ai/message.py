import reflex as rx


class Message(rx.Base):
    """A message to send to the agent."""

    role: str
    content: str
    type: str = "text"


class UserMessage(Message):
    """A message from the user."""

    role = "user"


class SystemMessage(Message):
    """A message from the system."""

    role = "system"


class AIMessage(Message):
    """A message from the AI."""

    role = "assistant"


class ToolMessage(Message):
    """A message from a tool."""

    role = "tool"
