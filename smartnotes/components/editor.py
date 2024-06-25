import reflex as rx


class Editor(rx.Component):
    library = "@mdxeditor/editor"

    tag = "MDXEditor"


    def add_imports(self):
        return {"": ["reactflow/dist/style.css"]}
