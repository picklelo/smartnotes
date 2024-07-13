import reflex as rx
from typing import Callable


import inspect
from typing import Any, Dict, Callable


class ToolInvocation(rx.Base):
    """Structure to specify a tool and arguments to invoke it with."""

    tool: str
    params: Dict[str, Any]

class ToolResponse(rx.Base):
    """Structure to specify the result of a tool invocation."""

    invocation: ToolInvocation
    result: Any
    error: str | None


class Tool(rx.Base):
    description: str | None
    params: Dict[str, Any]
    return_type: Any
    _func: Callable

    @classmethod
    def parse_function_annotations(cls, func: Callable) -> Dict[str, str]:
        """Parse function annotations into a more readable format."""
        signature = inspect.signature(func)
        params = {
            name: param.annotation.__name__ if hasattr(param.annotation, '__name__') else 'No annotation'
            for name, param in signature.parameters.items()
        }
        return_type = signature.return_annotation.__name__ if hasattr(signature.return_annotation, '__name__') else 'No annotation'
        description = inspect.getdoc(func) or 'No description'
        return {
            "name": func.__name__,
            "description": description,
            "params": params,
            "return_type": return_type
        }

    @classmethod
    def from_function(cls, func: Callable):
        """Create a tool from a function."""
        annotations = cls.parse_function_annotations(func)
        return cls(
            **annotations,
            _func=func,
        )

def send_message(message: str) -> None:
    """Send a final message to the user. This should be done after all internal processing is completed."""
    print(f"Sending message: {message}")

def get_temperature(city: str) -> int:
    """Get the temperature of a city."""
    print(f"Getting temperature for {city}")
    return 75

import io
import contextlib

def run_python_code(code: str) -> str:
    """Run Python code and return the result. Make sure to include the entirety of what's needed, including imports, etc."""
    print(f"Running Python code: {code}")
    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        exec(code, locals(), locals())
        output = buf.getvalue()
    return output

def get_issues():
    import git

    issues = git.get_issues(sort="state", state="open")
    with open("issues-open.txt", "w") as f:
        for issue in issues:
            print(issue.number)
            print(issue.number, issue.state, issue.title, issue.state)
            if issue.state == "open":
                f.write(
                    f"{issue.number}, {issue.state}, {issue.title}, {issue.state}\n"
                )


def read_journal_entry(date: str) -> str:
    """Reads a journal entry for a given date.

    Args:
        date (str): The date in the format 'YYYY-MM-DD'.

    Returns:
        str: The content of the journal entry or an error message if the file does not exist.
    """
    print(date)
    year, month_day = date.split("-")[:2]
    file_path = (
        f"/Users/nikhil/Documents/Vault/journal/{year}/{year}-{month_day}/{date}.md"
    )

    try:
        print("open", file_path)
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return "Journal entry not found for the specified date."
