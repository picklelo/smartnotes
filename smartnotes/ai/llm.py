from __future__ import annotations

import os
from typing import AsyncGenerator, Type

import reflex as rx
from smartnotes.ai import message


class Client:
    """A base class for language models."""

    async def stream_chat_lines(
        self,
        messages: list[message.Message],
        system: message.SystemMessage | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream the response from the chat model line by line.

        Args:
            messages: The messages to send to the model.

        Returns:
            An async generator yielding the response from the model line by line.
        """
        buffer = ""
        async for delta in self.stream_chat_response(messages, system=system):
            buffer += delta
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                yield line + "\n"


def to_llm_message(messages: list[message.Message]) -> list[dict]:
    """Convert the messages to a format that can be sent to the LLM.

    Args:
        messages: The messages to convert.

    Returns:
        The messages in a format that can be sent to the LLM.
    """
    return [m.to_llm_message() for m in messages]


class AnthropicClient(Client):
    def __init__(
        self, model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
    ):
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic()
        self.model = model
        self.max_tokens = 4096

    async def get_chat_response(
        self,
        messages: list[message.Message],
        system: message.SystemMessage | None = None,
    ) -> message.AIMessage:
        """Get the response from the chat model.

        Args:
            messages: The messages to send to the model.

        Returns:
            The response from the model.
        """
        system = system or message.SystemMessage(content="")
        content = (
            (
                await self.client.messages.create(
                    max_tokens=self.max_tokens,
                    messages=to_llm_message(messages),
                    model=self.model,
                    system=system.content,
                )
            )
            .content[0]
            .text
        )
        return message.AIMessage(content=content)

    async def stream_chat_response(
        self,
        messages: list[message.Message],
        system: message.SystemMessage | None = None,
    ) -> AsyncGenerator[message.AIMessage, None]:
        """Stream the response from the chat model.

        Args:
            messages: The messages to send to the model.

        Returns:
            An async generator yielding the response from the model.
        """
        system = system or message.SystemMessage(content="")
        ai_message = message.AIMessage(content="")
        async with self.client.messages.stream(
            max_tokens=self.max_tokens,
            messages=to_llm_message(messages),
            model=self.model,
            system=system.content,
        ) as stream:
            async for text in stream.text_stream:
                ai_message.content += text
                yield ai_message

    async def get_structured_response(
        self, messages: dict, model: Type[rx.Base]
    ) -> Type[rx.Base]:
        """Get the structured response from the chat model.

        Args:
            messages: The messages to send to the model.
            model: The model to use for the response.

        Returns:
            The structured response from the model.
        """
        system_prompt = f"""{messages[0]["content"]}

Return your answer according to the 'properties' of the following schema:
{model.schema()}

Return only the JSON object with the properties filled in.
Do not include anything in your response other than the JSON object.
Do not begin your response with ```json or end it with ```.
"""
        messages = [system_prompt] + messages[1:]
        response = await self.get_chat_response(messages)
        obj = model.load_raw(response)
        return obj


llm = AnthropicClient()
