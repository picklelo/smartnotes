import os
import reflex as rx


class ContextState(rx.State):
    selected_files: list[str]

    def add_file(self, data: dict[str, str]):
        filename = data["context-file"]
        if not os.path.exists(filename):
            return rx.toast.error(f"File {filename} does not exist.")
        if filename in self.selected_files:
            return rx.toast.error(f"File {filename} is already selected.")
        self.selected_files.append(filename)

    def remove_file(self, filename):
        self.selected_files.remove(filename)

    def _get_context(self):
        # Create a dict from filename to content.
        contents = {
            filename: open(filename).read()
            for filename in self.selected_files
        }
        return f"""Use the following context to answer: {'\n'.join(contents.values())}"""


def input_field():
    return rx.el.input(
        type="text",
        name="context-file",
        placeholder="Add file context",
        _focus={
            "--ring-color": rx.color("accent", 3),
            "box-shadow": "var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color)",
            "outline-style": "none",
        },
        border_width="1px",
        padding_left="0.75rem",
        padding_right="0.75rem",
        flex_grow="1",
        padding_top="0.5rem",
        padding_bottom="0.5rem",
        border_color=rx.color("gray", 5),
        border_radius="0.375rem",
    )


def file_tag(filename):
    return rx.badge(
        rx.flex(
            rx.icon(
                tag="x", 
                size=10,
                on_click=lambda: ContextState.remove_file(filename),
                _hover={
                    "cursor": "pointer",
                }
            ),
            rx.text(filename),
            spacing="1",
            align="center",
        ),
    )


def file_tag_list():
    return rx.flex(
        rx.foreach(
            ContextState.selected_files,
            file_tag,
        ),
        background_color=rx.color("gray", 1),
        overflow_y="auto",
        padding="0.5rem",
        max_height="10rem",
        box_shadow="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        border_radius="0.375rem",
    )


def tip_box():
    return rx.box(
        "Tip: Add files to enhance your RAG query context. Remove files to refine your search.",
        color=rx.color("gray", 8),
        margin_top="0.5rem",
        font_size="0.75rem",
        line_height="1rem",
    )


def form_box():
    return rx.form(
        rx.flex(
            input_field(),
            margin_bottom="1rem",
            display="flex",
            align_items="center",
            column_gap="0.5rem",
        ),
        on_submit=ContextState.add_file,
        reset_on_submit=True,
    )


def selected_files_box():
    return rx.box(
        "Selected files:",
        rx.text.span(ContextState.selected_files.length(), font_weight="700"),
        color=rx.color("gray", 8),
        font_size="0.875rem",
        line_height="1.25rem",
        margin_bottom="0.5rem",
    )


def file_context():
    return rx.fragment(
        rx.box(
            form_box(),
            selected_files_box(),
            file_tag_list(),
            tip_box(),
            background_color=rx.color("gray", 2),
            padding="1rem",
            border_radius="0.5rem",
            box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        )
    )
