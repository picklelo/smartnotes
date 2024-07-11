from __future__ import annotations

import json

from smartnotes.ai import llm, message
from smartnotes.ai import tool as tool_list
from smartnotes.ai.tool import tool, ToolInvocation, ToolResponse

import linear
import git


class Agent:
    def __init__(
        self,
        llm: llm.Client = llm.llm,
        system: message.SystemMessage | None = None,
        tools: list[tool.Tool] | None = None,
    ):
        self.system = system or message.SystemMessage(content="")
        self.scratchpad: list[ToolResponse] = []
        self.llm = llm
        self.tools = tools or [tool_list.send_message, tool_list.get_temperature, tool_list.run_python_code,
            linear.get_projects,
            linear.get_issues,
            tool_list.read_journal_entry,
            git.get_github_issues,
        ]
        print(self.tools)

    def modify_messages(self, messages: list[message.Message]):
        return messages

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
            result = tool._func(**response.params)
            tool_response = ToolResponse(invocation=response, result=result, error=None)
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
        print("original system")
        print(system)
        if len(self.context_files) > 0:
            system.content = f"{system}\nUse the following files as context: {self.context_files}"
        return system
