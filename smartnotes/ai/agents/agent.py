from __future__ import annotations

import json

from smartnotes.ai import llm, message
from smartnotes.ai.tool import Tool, ToolInvocation, ToolResponse
from typing import Callable

class Agent:
    def __init__(
        self,
        llm: llm.Client = llm.llm,
        prompt: str = "",
        tools: list[Callable] | None = None,
    ):
        self.system = message.SystemMessage(content=prompt)
        self.scratchpad: list[ToolResponse] = []
        self.llm = llm
        self.tools = tools or []
        self.tools = [Tool.from_function(tool) for tool in self.tools]

    def modify_messages(self, messages: list[message.Message]):
        # Go back 10 user messages.
        user_messages = [message for message in messages if message.role == "user"]
        print(user_messages)
        start_message = max(len(user_messages) - 10, 0)
        start_index = messages.index(user_messages[start_message])
        return messages[start_index:]

    def get_system_message(self) -> message.SystemMessage:
        system = self.system
        if len(self.tools) > 0:
            print("tools")
            print(self.tools)
            system = f"""{system}
You have the following tools available:
{"\n".join([json.dumps([tool.dict(exclude={"_func"}) for tool in self.tools], indent=2)])}
Make sure your response includes only one of these valid tools.
"""
        if len(self.scratchpad) > 0:
            system = f"""{system}
The current scratchpad output of tool invocation responses is:
{"\n".join([json.dumps([response.dict(exclude={"invocation._func"}) for response in self.scratchpad], indent=2)])}
"""
        print(system)
        return message.SystemMessage(content=system)

    async def stream(self, messages: list[message.Message]):
        system = self.get_system_message()
        messages = self.modify_messages(messages)

        while True:
            print("messages")
            print(messages)
            response = await self.llm.get_structured_response(messages, model=ToolInvocation, system=system)
            assert isinstance(response, ToolInvocation), f"Expected a ToolInvocation response, got {response}"
            # Base case
            if response.tool == "send_message":
                yield message.AIMessage(content=response.params["message"])
                return
            ai_message = message.AIMessage(content=json.dumps(response.dict(), indent=2))
            messages.append(ai_message)
            print(ai_message)

            yield ai_message
            tool = [tool for tool in self.tools if tool.name == response.tool][0]
            # Invoke the tool.
            try:
                result = tool._func(**response.params)
                tool_response = ToolResponse(invocation=response, result=result, error=None)
            except Exception as e:
                result = str(e)
                tool_response = ToolResponse(invocation=response, result=None, error=result)
            self.scratchpad.append(tool_response)
            user_message = message.UserMessage(content=f"Tool invocation response: {result}")
            messages.append(user_message)
            yield user_message
        # async for ai_message in self.llm.stream_chat_response(messages, system=system):
        #     messages[-1] = ai_message
        #     yield ai_message

    async def get_response(self, messages: list[message.Message]):
        system = self.get_system_message()
        messages = self.modify_messages(messages)
        print("messages", messages)
        print("system", system)
        return await self.llm.get_chat_response(messages, system=system)


class ConversationNameAgent(Agent):
    def modify_messages(self, messages: list[message.Message]):
        assert len(messages) > 0, "No messages provided."
        first_message = messages[0].content
        prompt = f"""Given the following first message to this conversation, give it a short, succinct title: {first_message}.\n Include only the title, nothing else. Do not include any text other than the new title."""
        return [message.UserMessage(content=prompt)]

class ContextAgent(Agent):
    def __init__(self, context_files: dict[str, str], **kwargs):
        super().__init__(**kwargs)
        self.context_files = context_files

    def get_system_message(self) -> message.SystemMessage:
        system = super().get_system_message()
        print("original system")
        print(system)
        if len(self.context_files) > 0:
            system.content = f"{system}\nUse the following files as context: {self.context_files}"
        return system
