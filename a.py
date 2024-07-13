import reflex as rx
from smartnotes.ai.agents.agent import Agent
from smartnotes.ai.tool import send_message
from tools import tool_management, websearch, email, coder_tools


agent = Agent(
    prompt="""You are a code editing agent to help understand and edit code.""",
    tools=[
        tool_management.list_all_tools,
        coder_tools.read_source_file,
        coder_tools.update_function_source,
        coder_tools.add_function_to_file,
        coder_tools.create_directory,
        coder_tools.create_file,
        email.read_emails,
        websearch.search_web,
        websearch.read_webpage,
        send_message,
    ]
)