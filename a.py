import reflex as rx
from smartnotes.ai import tool

print(tool.get_issues.dict(exclude={"func"}))
print(tool.send_message)
print(tool.ToolInvocation.schema())

import linear
print(linear.get_project_info._func("Improved init workflow"))