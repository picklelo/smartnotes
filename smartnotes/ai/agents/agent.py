from __future__ import annotations
from smartnotes.ai import llm, message
from smartnotes.ai.tool import tool


class Agent:
    def __init__(
        self,
        llm: llm.Client = llm.llm,
        system: message.SystemMessage | None = None,
        tools: list[tool.Tool] | None = None,
    ):
        self.system = system or message.SystemMessage(content="")
        self.scratchpad = {}
        self.llm = llm
        self.tools = tools or []

    def modify_messages(self, messages: list[message.Message]):
        return messages

    def get_system_message(self) -> message.SystemMessage:
        tools_message = """You have the following tools available:
{"\n".join([t.sc])}
        """
        return self.system

    async def stream(self, messages: list[message.Message]):
        system = self.get_system_message()
        messages = self.modify_messages(messages)
        async for ai_message in self.llm.stream_chat_response(messages, system=system):
            messages[-1] = ai_message
            yield ai_message

    async def get_response(self):
        system = self.get_system_message()
        messages = self.get_messages()
        return await self.llm.get_chat_response(messages, system=system)


class ConversationNameAgent(Agent):
    def modify_messages(self, messages: list[message.Message]):
        assert len(messages) > 0, "No messages provided."
        first_message = messages[0].content
        prompt = f"""Given the following first message to this conversation, give it a short, succinct title: {first_message}.\n Include only the title, nothing else."""
        return [message.UserMessage(content=prompt)]

class ContextAgent(Agent):
    def __init__(self, context_files: dict[str, str], **kwargs):
        super().__init__(**kwargs)
        self.context_files = context_files

    def get_system_message(self) -> message.SystemMessage:
        system = super().get_system_message()
        if len(self.context_files) > 0:
            system.content = f"Use the following files as context: {self.context_files}"
