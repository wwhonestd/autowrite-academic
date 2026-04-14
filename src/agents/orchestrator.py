from typing import List, Dict, Any
from src.agents.base import BaseAgent
from src.communication.protocol import Message

class OrchestratorAgent(BaseAgent):
    def __init__(self, agent_id: str | None = None):
        super().__init__("Orchestrator", agent_id)
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: List[Message] = []
        self.current_task: str | None = None

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.agent_id] = agent
        print(f"Agent {agent} registered.")

    def run_task(self, task_description: str):
        self.current_task = task_description
        print(f"Orchestrator starting task: {task_description}")
        # Logic to decompose task and assign to agents will go here

    def process_message(self, message: Message):
        self.message_queue.append(message)
        # Logic to route messages to appropriate agents or handle them centrally
        if message.sender_id in self.agents:
            print(f"Orchestrator received message from {self.agents[message.sender_id].name}")
        else:
            print(f"Orchestrator received message from unknown sender {message.sender_id[:6]}...")

        # Example: route message to researcher if it's a research-related task
        # Note: This assumes a 'researcher' agent is registered and has a 'receive_message' method.
        # This part will be expanded when ResearcherAgent is implemented.
        if "research" in message.content.lower() and "researcher" in self.agents:
            try:
                self.agents["researcher"].receive_message(message)
            except AttributeError:
                print("Researcher agent does not have receive_message method yet.")

    def run(self, *args, **kwargs):
        # This method might be used for the main loop or high-level task execution
        if self.current_task:
            self.run_task(self.current_task)
        else:
            print("Orchestrator is idle.")

    def stop(self):
        print(f"Stopping Orchestrator ({self.agent_id[:6]}...)")
        for agent in self.agents.values():
            agent.stop()
        super().stop()
