import reflex as rx
from smartnotes.ai.message import (
    Conversation,
    Message,
    UserMessage,
)
from sqlmodel import select
from smartnotes.components.file_context import ContextState
from smartnotes.ai.agents import agent

DEFAULT_CONVERSATIION_NAME = "Chat"

@rx.memo
def markdown(content: str):
    return rx.markdown(content)


class ChatState(rx.State):
    conversations: list[Conversation] = []
    current_conversation: Conversation = Conversation(name=DEFAULT_CONVERSATIION_NAME)
    messages: list[Message] = []

    async def name_conversation(self):
        if self.current_conversation.name != DEFAULT_CONVERSATIION_NAME:
            return
        convo_agent = agent.ConversationNameAgent()
        response = await convo_agent.get_response(self.messages[:1])
        with rx.session() as session:
            self.current_conversation.name = response.content
            session.add(self.current_conversation)
            session.commit()
            session.refresh(self.current_conversation)

    def select_conversation(self, conversation_id):
        with rx.session() as session:
            self.current_conversation = session.get(Conversation, conversation_id)
            self.messages = session.exec(
                select(Message)
                .filter(Message.conversation_id == self.current_conversation.id)
                .order_by(Message.id)
            ).all()

    def new_conversation(self):
        with rx.session() as session:
            self.conversations.insert(0, Conversation(name="Chat"))
            # self.conversations.append(Conversation(name="Chat"))
            session.add(self.conversations[0])
            session.commit()
            session.refresh(self.conversations[0])
            self.current_conversation = self.conversations[0]
            self.messages = session.exec(
                select(Message)
                .filter(Message.conversation_id == self.current_conversation.id)
                .order_by(Message.id)
            ).all()

    def delete_conversation(self, conversation_id):
        with rx.session() as session:
            session.delete(Conversation, conversation_id)
            session.commit()
        self.conversations = [
            c for c in self.conversations if c.id != conversation_id
        ]
        if len(self.conversations) == 0:
            self.new_conversation()

    async def on_load(self):
        # Get the most recent conversation.
        with rx.session() as session:
            self.conversations = session.exec(
                select(Conversation).order_by(Conversation.id.desc())
            ).all()
            if len(self.conversations) == 0:
                self.conversations.append(Conversation(name="Chat"))
                session.add(self.conversations[0])
                session.commit()
                session.refresh(self.conversations[0])
            self.select_conversation(self.conversations[0].id)

    async def process_message(self, data: dict[str, str]):
        message = data["user-input"]
        self.messages.append(
            UserMessage(content=message, conversation_id=self.current_conversation.id)
        )
        # self.messages.append(
        #     AIMessage(content="", conversation_id=self.current_conversation.id)
        # )
        yield

        from a import agent as context_agent

        context_state = await self.get_state(ContextState)
        # context_agent = agent.ContextAgent(
        #     context_files=context_state._get_context(),
        #     tools=[
        #         tool.send_message, 
        #         # tool_list.get_temperature, tool_list.run_python_code,
        #         linear.get_projects,
        #         linear.get_issues,
        #         linear.get_project_info,
        #         linear.get_component_docs,
        #     ]
        # )
        message_index = len(self.messages)
        async for message in context_agent.stream(self.messages.copy()):
            message.conversation_id = self.current_conversation.id
            self.messages.append(message)
            yield
        with rx.session() as session:
            print("adding messages", self.messages[-2], self.messages[-1])
            for message in self.messages[message_index:]:
                session.add(message)
            # session.add(self.messages[-2])
            # session.add(self.messages[-1])
            session.commit()
            for message in self.messages[message_index:]:
                session.refresh(message)
        # await self.name_conversation()


def common_button(icon, color, hover_color, **kwargs):
    return rx.el.button(
        rx.icon(icon),
        transition_property="color, background-color, border-color, text-decoration-color, fill, stroke",
        transition_timing_function="cubic-bezier(0.4, 0, 0.2, 1)",
        transition_duration="300ms",
        _hover={"color": hover_color},
        color=color,
        **kwargs
    )

@rx.memo
def markdown(content: str):
    return rx.markdown(
        content,
        color=rx.color("gray", 11),
        font_size="0.875rem",
        line_height="1.25rem",
    )


def chat_message(message: Message):
    bg_color = rx.cond(
        message.role == "user",
        rx.color("plum", 4),
        rx.color("accent", 4),
    )
    justify = rx.cond(
        message.role == "user",
        "flex-end",
        "flex-start",
    )
    should_show = (message.role == "user") | (message.role == "assistant")
    return rx.cond(
        should_show,
        rx.flex(
            rx.box(
                markdown(content=message.content),
                border_radius="1rem",
                background_color=bg_color,
                padding_left="1rem",
                padding_right="1rem",
                max_width="65%",
                box_shadow="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                padding_top="0.5rem",
                padding_bottom="0.5rem",
                background_image="background-image",
            ),
            display="flex",
            justify_content=justify,
        ),
    )


def chat_container():
    return rx.scroll_area(
        rx.flex(
            rx.foreach(ChatState.messages, lambda message: chat_message(message)),
            id="chat-container",
            overflow_y="auto",
            flex="1 1 0%",
            gap="1rem",
            display="flex",
            flex_direction="column",
            padding="1rem",
        )
    )


def header_section():
    return rx.flex(
        rx.box(
            width="2.5rem",
            background_color=rx.color("accent", 5),
            border_radius="9999px",
            height="2.5rem",
            background_image="background-image",
        ),
        rx.el.h1(
            ChatState.current_conversation.name,
            font_size="1.25rem",
            line_height="1.75rem",
            color=rx.color("gray", 11),
            font_weight="200",
        ),
        align_items="center",
        display="flex",
        column_gap="0.875rem",
    )


def header():
    return rx.flex(
        header_section(),
        border_bottom_width="1px",
        justify_content="space-between",
        align_items="center",
        background_color=rx.color("gray", 1),
        __bg_opacity="0.7",
        backdrop_blur="blur(12px)",
        border_color=rx.color("gray", 1),
        display="flex",
        padding="1rem",
    )


def input_section():
    return rx.box(
        rx.form(
            rx.flex(
                common_button("paperclip", rx.color("gray", 8), rx.color("gray", 10)),
                rx.text_area(
                    name="user-input",
                    type="text",
                    placeholder="Type your message...",
                    _focus={
                        "--ring-color": rx.color("accent", 3),
                        "outline-style": "none",
                        "box-shadow": "var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color)",
                    },
                    auto_height=True,
                    rows="1",
                    min_height=0,
                    enter_key_submit=True,
                    color=rx.color("gray", 11),
                    padding_left="1rem",
                    padding_right="1rem",
                    transition_property="all",
                    transition_timing_function="cubic-bezier(0.4, 0, 0.2, 1)",
                    transition_duration="300ms",
                    font_size="0.875rem",
                    line_height="1.25rem",
                    flex="1 1 0%",
                    # border_radius="var(--radius-4)",
                    padding_x="1em",
                    border_radius="20px",
                    background_color=rx.color("gray", 1),
                    padding_top="0.5rem",
                    padding_bottom="0.5rem",
                ),
                common_button("send", rx.color("accent", 8), rx.color("accent", 9)),
                align_items="center",
                column_gap="0.5rem",
                display="flex",
            ),
            border_top_width="1px",
            border_color=rx.color("gray", 1),
            background_color=rx.color("gray", 1),
            padding="1rem",
            on_submit=ChatState.process_message,
            reset_on_submit=True,
        )
    )


def chat():
    return rx.flex(
        header(),
        chat_container(),
        input_section(),
        background_color=rx.color("gray", 1),
        overflow="hidden",
        box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        border_radius="1rem",
        width="100%",
        height="95vh",
        flex_direction="column",
        background_image="background-image",
        display="flex",
        on_mount=ChatState.on_load,
    )
