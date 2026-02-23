# Tool Registry
# Part of thegent-mcp sub-project

class ToolRegistry:
    """Registry for MCP tools."""
    
    def __init__(self):
        self.tools = {}
        
    def register(self, name: str, handler):
        """Register a tool handler."""
        self.tools[name] = handler
        
    def get(self, name: str):
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self):
        """List all registered tools."""
        return list(self.tools.keys())

# Global tool registry
tool_registry = ToolRegistry()

# Register default tools
tool_registry.register("execute_task", lambda **kwargs: {"result": "executed"})
tool_registry.register("list_tasks", lambda **kwargs: {"result": []})
tool_registry.register("get_status", lambda **kwargs: {"result": "ok"})
