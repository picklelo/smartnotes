import reflex as rx
from typing import Callable


import inspect
from typing import Any, Dict, Callable
import pydantic

class ToolInvocation(rx.Base):
    """Structure to specify a tool and arguments to invoke it with."""

    tool: str
    params: Dict[str, Any]

class Tool(rx.Base):
    params: Dict[str, Any]
    return_type: Any
    func: Callable

    @classmethod
    def parse_function_annotations(cls, func: Callable) -> Dict[str, Any]:
        """Parse function annotations."""
        signature = inspect.signature(func)
        params = {name: param.annotation for name, param in signature.parameters.items()}
        return_type = signature.return_annotation
        return {
            "params": params,
            "return_type": return_type
        }

    @classmethod
    def from_function(cls, func: Callable):
        """Create a tool from a function."""
        annotations = cls.parse_function_annotations(func)
        return cls(
            params=annotations["params"],
            return_type=annotations["return_type"],
            func=func
        )

def tool(func):
    print("tool", func)
    return Tool.from_function(func)


@tool
def send_message(message: str) -> None:
    """Send a final message to the user. This should be done after all internal processing is completed."""
    print(f"Sending message: {message}")

@tool
def get_issues():
    import git
    issues = git.get_issues(sort="state", state="open")
    with open("issues-open.txt", "w") as f:
        for issue in issues:
            print(issue.number)
            print(issue.number, issue.state, issue.title, issue.state)
            if issue.state == "open":
                f.write(f"{issue.number}, {issue.state}, {issue.title}, {issue.state}\n")