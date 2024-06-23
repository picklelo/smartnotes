import reflex as rx
from smartnotes.ai.llm import llm
from smartnotes.ai.message import Message, SystemMessage, UserMessage, AIMessage

class ChatState(rx.State):
    messages: list[Message] = [
        SystemMessage(content="You are a helpful assistant."),
    ]

    async def process_message(self, data: dict[str, str]):
        message = data["user-input"]
        self.messages.append(UserMessage(content=message))
        self.messages.append(AIMessage(content=""))
        async for chunk in llm.stream_chat_response(self.messages):
            self.messages[-1].content += chunk
            yield


def common_button(icon, color, hover_color):
    return rx.el.button(
        rx.icon(icon),
        transition_property="color, background-color, border-color, text-decoration-color, fill, stroke",
        transition_timing_function="cubic-bezier(0.4, 0, 0.2, 1)",
        transition_duration="300ms",
        _hover={"color": hover_color},
        color=color,
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
                rx.text(message.content, color=rx.color("gray", 11), font_size="0.875rem", line_height="1.25rem"),
                border_radius="1rem",
                background_color=bg_color,
                padding_left="1rem",
                padding_right="1rem",
                max_width="32rem",
                box_shadow="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                padding_top="0.5rem",
                padding_bottom="0.5rem",
                background_image="background-image",
            ),
            display="flex",
            justify_content=justify,
        )
    )


def chat_container():
    return rx.flex(
        rx.foreach(
            ChatState.messages,
            lambda message: chat_message(message)
        ),
        id="chat-container",
        overflow_y="auto",
        flex="1 1 0%",
        gap="1rem",
        display="flex",
        flex_direction="column",
        padding="1rem"
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
            "Futuristic Chat",
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
                rx.el.input(
                    name="user-input",
                    type="text",
                    placeholder="Type your message...",
                    _focus={
                        "--ring-color": rx.color("accent", 3),
                        "outline-style": "none",
                        "box-shadow": "var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color)",
                    },
                    color=rx.color("gray", 11),
                    padding_left="1rem",
                    padding_right="1rem",
                    transition_property="all",
                    transition_timing_function="cubic-bezier(0.4, 0, 0.2, 1)",
                    transition_duration="300ms",
                    font_size="0.875rem",
                    line_height="1.25rem",
                    flex="1 1 0%",
                    border_radius="9999px",
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
        height="100%",
        flex_direction="column",
        background_image="background-image",
        display="flex",
    )
