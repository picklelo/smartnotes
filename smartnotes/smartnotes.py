import reflex as rx
from smartnotes.components.chat import chat, ChatState
from reflex_resizable_panels import resizable_panels as rzp


def test():
    return rx.fragment(
        rx.color_mode.button(position="top-right"),
        rzp.group(
            rzp.panel(
                sidebar(),
                min_size=25,
                default_size=25,
            ),
            rzp.handle(),
            rzp.panel(
                main_content(),
                min_size=50,
            ),
            direction="horizontal",
            display="flex",
            height="100vh",
        ),
    )


def avatar(src, alt, height, width, margin_right=None):
    return rx.image(
        src=src,
        alt=alt,
        border_radius="9999px",
        height=height,
        width=width,
        margin_right=margin_right,
    )


def conversation(conversation):
    return rx.box(
        rx.flex(
            avatar(
                src="https://placehold.co/40x40",
                alt="Contact avatar",
                height="2.5rem",
                width="2.5rem",
                margin_right="0.75rem",
            ),
            rx.box(
                rx.el.h3(conversation.name, font_weight="600"),
                rx.text(
                    rx.moment(conversation.timestamp),
                    font_size="0.875rem",
                    line_height="1.25rem",
                    color=rx.color("gray", 10),
                ),
            ),
            display="flex",
            align_items="center",
        ),
        background_color=rx.cond(
            ChatState.current_conversation.id == conversation.id,
            rx.color("accent", 2),
            rx.color("gray", 1),
        ),
        cursor="pointer",
        _hover={"background-color": rx.color("gray", 3)},
        padding="1rem",
        on_click=lambda: ChatState.select_conversation(conversation.id),
    )


def top_bar():
    return rx.box(
        rx.flex(
            rx.image(
                src="https://placehold.co/100x40",
                alt="Chat app logo",
                height="2.5rem",
            ),
            rx.flex(
                avatar(
                    src="https://placehold.co/40x40",
                    alt="User avatar",
                    height="2rem",
                    width="2rem",
                ),
                display="flex",
                align_items="center",
            ),
            display="flex",
            align_items="center",
            justify_content="space-between",
        ),
        border_bottom_width="1px",
        padding="1rem",
    )


def search_box():
    return rx.hstack(
        rx.el.input(
            type="text",
            placeholder="Search conversations",
            _focus={
                "--ring-color": rx.color("accent", 10),
                "outline-style": "none",
                "box-shadow": "var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color)",
            },
            padding_left="2.5rem",
            width="100%",
            border_radius="0.5rem",
            padding_top="0.5rem",
            padding_bottom="0.5rem",
            padding_right="1rem",
            border_width="1px",
        ),
        rx.button(
            rx.icon("plus"),
            variant="outline",
            on_click=ChatState.new_conversation,
        ),
        align="center",
        position="relative",
        padding="1rem",
    )


def sidebar():
    return rx.vstack(
        rx.logo(),
        search_box(),
        rx.box(
            rx.foreach(ChatState.conversations, conversation),
            overflow_y="auto",
        ),
        rx.spacer(),
        style={"@media (min-width: 1024px)": {"display": "block"}},
        display="none",
        background_color=rx.color("gray", 1),
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        height="100vh",
    )


def main_content():
    return rx.flex(
        rx.center(
            chat(), flex="1 1 0%", background_color=rx.color("gray", 1), padding="1rem"
        ),
        flex="1 1 0%",
        flex_direction="column",
        display="flex",
    )


def icon_button(margin_left=None):
    return rx.el.button(
        padding="0.5rem",
        _hover={"background-color": rx.color("gray", 3)},
        border_radius="9999px",
        margin_left=margin_left,
    )


app = rx.App(theme=rx.theme(accent_color="sky"))
app.add_page(test, route="/")
