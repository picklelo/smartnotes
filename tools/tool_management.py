import os


base_path = os.path.dirname(os.path.abspath(__file__))


def list_all_tools():
    import os
    import ast

    from collections import defaultdict

    tools = defaultdict(list)
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            args = [a.arg for a in node.args.args]
                            signature = f"{node.name}({', '.join(args)})"
                            tools[file].append(signature)
    grouped_tools = [f"{file}: {', '.join(funcs)}" for file, funcs in tools.items()]
    return grouped_tools


def read_source_file(file_path: str) -> str:
    """Read the contents of a source file."""
    file_path = os.path.join(base_path, file_path)
    with open(file_path, "r") as f:
        return f.read()


def add_function_to_file(file_path: str, function_code: str) -> str:
    """Add a function to a file."""
    file_path = os.path.join(base_path, file_path)
    with open(file_path, "a") as f:
        f.write(function_code)
    return f"Function added to the file."


def update_function_source(file_path: str, function_name: str, new_code: str) -> str:
    """Modify the source code of a function in a file."""
    file_path = os.path.join(base_path, file_path)
    with open(file_path, "r") as f:
        lines = f.readlines()
    start_line = None
    end_line = None
    for i, line in enumerate(lines):
        if f"def {function_name}(" in line:
            start_line = i
        if start_line is not None and line.strip() == "":
            end_line = i
            break
    if start_line is None:
        return f"Function '{function_name}' not found in the file."

    new_lines = lines[:start_line] + new_code.split("\n") + ["\n"] + lines[end_line:]
    with open(file_path, "w") as f:
        f.writelines(new_lines)
    return f"Function '{function_name}' updated in the file."
