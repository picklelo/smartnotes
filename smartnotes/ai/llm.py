import os
from typing import AsyncGenerator

from smartnotes.ai.message import Message, UserMessage, AIMessage


class LLM:
    """A base class for large language models."""

    @classmethod
    def format_message(cls, message: Message) -> dict:
        """Format a message for the model.

        Args:
            message: The message to format.

        Returns:
            The formatted message.
        """
        return {"role": message.role, "content": message.content}

    @classmethod
    def format_messages(cls, message: list[Message]) -> dict:
        """Format a message for the model.

        Args:
            message: The message to format.

        Returns:
            The formatted message.
        """
        return [cls.format_message(m) for m in message]

    async def stream_chat_lines(
        self, messages: list[Message]
    ) -> AsyncGenerator[str, None]:
        """Stream the response from the chat model line by line.

        Args:
            messages: The messages to send to the model.

        Returns:
            An async generator yielding the response from the model line by line.
        """
        buffer = ""
        async for delta in self.stream_chat_response(messages):
            buffer += delta
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                yield line + "\n"


class AnthropicClient(LLM):
    def __init__(
        self, model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
    ):
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic()
        self.model = model

    async def get_chat_response(self, messages: list[Message]) -> str:
        """Get the response from the chat model.

        Args:
            messages: The messages to send to the model.

        Returns:
            The response from the model.
        """
        system_messages = [m for m in messages if m.role == "system"]
        messages = [m for m in messages if isinstance(m, UserMessage) or isinstance(m, AIMessage)]
        system = system_messages[-1].content if system_messages else None
        breakpoint()
        return (
            (
                await self.client.messages.create(
                    max_tokens=4096,
                    messages=self.format_messages(messages),
                    model=self.model,
                    system=system
                )
            )
            .content[0]
            .text
        )

    async def stream_chat_response(self, messages: list[Message]) -> AsyncGenerator[str, None]:
        """Stream the response from the chat model.

        Args:
            messages: The messages to send to the model.

        Returns:
            An async generator yielding the response from the model.
        """
        system_messages = [m for m in messages if m.role == "system"]
        messages = [m for m in messages if m.role in ["user", "ai"]]
        system = system_messages[-1].content if system_messages else None
        async with self.client.messages.stream(
            max_tokens=4096,
            messages=self.format_messages(messages),
            model=self.model,
            system=system,
        ) as stream:
            async for text in stream.text_stream:
                yield text


llm = AnthropicClient()
