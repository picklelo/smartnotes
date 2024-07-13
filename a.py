import reflex as rx
from smartnotes.ai.agents.agent import Agent
from smartnotes.ai.tool import send_message
from tools import file_editing, websearch


agent = Agent(
    prompt="""You are a code editing agent to help understand and edit code.""",
    tools=[
        file_editing.list_all_tools,
        file_editing.read_source_file,
        file_editing.update_function_source,
        file_editing.add_function_to_file,
        websearch.search_web,
        websearch.read_webpage,
        send_message,
    ]
)