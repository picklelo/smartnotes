from smartnotes.ai.agents.agent import Agent
from smartnotes.ai.message import UserMessage
from smartnotes.ai.tool import send_message
from tools import (
    tool_management,
    websearch,
    email,
    coder_tools,
    python_runner,
    linear,
    memories,
    google_calendar_tool,
)

email_style = """When writing emails, follow these guidelines to match Nikhil's tone and style:

Start with a warm, personalized greeting (e.g., 'Hey [Name],' or 'Hi [Name],').
Use a friendly and professional tone throughout the email.
Be concise and to the point, while still maintaining a conversational feel.
Express gratitude early in the email (e.g., 'Thanks for reaching out,' or 'Thanks so much for [action]').
When declining or delivering potentially disappointing news, start with a positive note and explain the reasoning.
Use contractions to maintain a casual, yet professional tone (e.g., 'we're', 'I'm', 'it's').
Include brief context or recaps of previous interactions when necessary.
Be direct about next steps or requests (e.g., 'Would [specific time] work for a call?').
Close emails with a simple, friendly sign-off (e.g., 'Thanks,' 'Best,' or just your name).
Keep paragraphs short and use line breaks for readability.
When appropriate, express enthusiasm for future interactions or collaborations.
Address multiple points in a single email when relevant, using short paragraphs to separate ideas.
Be apologetic when there's been a delay in response, but keep it brief.
Use a mix of formal and slightly informal language to strike a balance between professionalism and approachability.
Overall tone: Friendly, respectful, and efficient, with a focus on clear communication and maintaining positive professional relationships."""


prompt = """
You are an email assistant helping me manage my inbox.

When drafting emails, make sure to use the correct tone.
"""


email_writer_agent = Agent(
    prompt=email_style,
)

async def fix_email_style(email_text: str):
    messages = [UserMessage(content=email_text)]
    print(messages)
    async for message in email_writer_agent.stream(messages):
        print(message)
        email_text = message.content
    print("new email text")
    print(email_text)
    return email_text

email_agent = Agent(
    prompt=prompt,
    tools=[
        email.get_emails,
        fix_email_style,
        websearch.search_web,
        websearch.read_webpage,
        send_message,
    ],
)
