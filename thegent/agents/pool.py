# Agent Pool
# Part of thegent-agents sub-project


class AgentPool:
    """Manages agent pool for task execution."""

    def __init__(self, max_agents: int = 4):
        self.max_agents = max_agents
        self.available = max_agents

    async def acquire(self):
        """Acquire an agent from the pool."""
        if self.available > 0:
            self.available -= 1
            return True
        return False

    def release(self):
        """Release an agent back to the pool."""
        if self.available < self.max_agents:
            self.available += 1

    def status(self):
        """Get pool status."""
        return {"available": self.available, "max": self.max_agents}
