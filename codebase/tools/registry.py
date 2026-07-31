from typing import Callable, Any, Dict

class Tool:
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
        
    def run(self, **kwargs) -> Any:
        return self.func(**kwargs)

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        
    def register(self, tool: Tool):
        self.tools[tool.name] = tool
        
    def get_tool_descriptions(self) -> str:
        return "\n".join([f"- {name}: {t.description}" for name, t in self.tools.items()])

# Placeholder for future tool registration
tool_registry = ToolRegistry()
