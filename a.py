import reflex as rx
from smartnotes.ai.agents.agent import Agent
from smartnotes.ai.tool import send_message
from tools import tool_management, websearch, email, coder_tools, python_runner, linear, memories, google_calendar_tool


agent = Agent(
    prompt="""You are a code editing agent to help understand and edit code.""",
    tools=[
        tool_management.list_all_tools,
        tool_management.read_tool_file,
        tool_management.create_tool,
        tool_management.update_tool,
        google_calendar_tool.get_calendar_events,
        # coder_tools.update_function_source,
        # coder_tools.add_function_to_file,
        # coder_tools.create_directory,
        # coder_tools.create_file,
        # coder_tools.read_file,
        python_runner.run_python_script,
        email.read_emails,
        websearch.search_web,
        websearch.read_webpage,
        linear.get_projects,
        linear.get_issues,
        linear.get_milestones,
        linear.get_team_members,
        memories.list_memories,
        memories.read_memory,
        memories.write_memory,
        memories.get_journal_entries,
        memories.read_journal_entry,
        send_message,
    ]
)