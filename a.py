from smartnotes.ai import tool

print(tool.get_issues.dict(exclude={"func"}))
print(tool.send_message)
print(tool.ToolInvocation.schema())