import abc
import uuid

class BaseAgent(abc.ABC):
    def __init__(self, name: str, agent_id: str | None = None):
        self.name = name
        self.agent_id = agent_id if agent_id else str(uuid.uuid4())

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        pass

    def stop(self):
        pass

    def communicate(self, message: str):
        # Placeholder for inter-agent communication
        print(f"Agent {self.name} ({self.agent_id[:6]}...): {message}")

    def __str__(self):
        return f"{self.name} ({self.agent_id[:6]}...)"
