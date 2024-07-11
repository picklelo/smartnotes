from smartnotes.ai.message import Message, UserMessage
from smartnotes.ai.llm import LLM


class Agent:
    def __init__(self, llm: LLM, initial_context=None):
        
        self.llm = llm

    async def stream_response(self, messages: list[Message]):
        async for chunk in self.llm.stream_chat_response(messages):
            messages[-1].content += chunk
            yield

class ContextAgent:
    """An agent that can use file context."""

    def __init__(self, llm: LLM, context=None):
        self.llm = llm
        self.context = context

    async def process(self, messages: list[Message]):
        # Update the system prompt with the context.
        assert isinstance(messages[-2], UserMessage)
        original_message = messages[-2].content
        messages[-2] = UserMessage(content=f"{original_message}\n{self.context}")

        async for _ in super().process(messages):
            yield
