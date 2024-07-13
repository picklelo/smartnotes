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
