def read_file_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def update_function_source(file_path, function_name, new_code):
    with open(file_path, "r") as file:
        content = file.read()
    import ast, astor

    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            new_func = ast.parse(new_code).body[0]
            node.body = new_func.body
    with open(file_path, "w") as file:
        file.write(astor.to_source(tree))
    return f"Function {function_name} updated in {file_path}"


def add_function_to_file(file_path, function_code):
    with open(file_path, "a") as file:
        file.write("\n\n" + function_code)
    return f"Function added to {file_path}"


def create_directory(directory_path: str) -> str:
    import os

    try:
        os.makedirs(directory_path, exist_ok=True)
        return f"Directory created successfully: {directory_path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


def create_file(file_path: str, content: str = "") -> str:
    """Create a new file with optional initial content.

    Args:
        file_path (str): The path where the new file should be created.
        content (str, optional): Initial content to write to the file. Defaults to empty string.

    Returns:
        str: A message indicating success or failure.
    """
    try:
        with open(file_path, "w") as file:
            file.write(content)
        return f"File '{file_path}' created successfully."
    except IOError as e:
        return f"Error creating file '{file_path}': {str(e)}"
