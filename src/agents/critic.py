from typing import List, Dict, Any
from .base import BaseAgent
from ..communication.protocol import Message

class CriticAgent(BaseAgent):
    def __init__(self, agent_id: str | None = None):
        super().__init__("Critic", agent_id)

    def evaluate_content(self, content: str, evaluation_criteria: List[str]) -> Dict[str, Any]:
        print(f"Critic evaluating content based on: {evaluation_criteria}")
        evaluation_result = {"scores": {}, "feedback": ""}
        # TODO: Implement LLM-based critique using evaluation_criteria
        # Example: Check for clarity, argument strength, counterarguments, etc.
        evaluation_result["scores"] = {"clarity": 2, "argument_strength": 1}
        evaluation_result["feedback"] = "Content is mostly clear but could benefit from stronger counterarguments."
        return evaluation_result

    def receive_message(self, message: Message):
        if "evaluate" in message.content.lower():
            parts = message.content.split(":")
            if len(parts) > 1:
                content_and_criteria = parts[1].strip()
                # Basic parsing: assume criteria are comma-separated after a semicolon
                if '; ' in content_and_criteria:
                    content, criteria_str = content_and_criteria.split('; ', 1)
                    criteria = [c.strip() for c in criteria_str.split(',') if c.strip()]
                    result = self.evaluate_content(content, criteria)
                    print(f"Critique result: {result}")
                else:
                    print("Invalid message format for critique.")
            else:
                print("Invalid message format for critique.")

    def run(self, *args, **kwargs):
        print("Critic agent is ready. Waiting for content evaluation requests.")

    def stop(self):
        print(f"Stopping Critic ({self.agent_id[:6]}...)")
        super().stop()
