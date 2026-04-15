from typing import List, Dict, Any
from .base import BaseAgent
from ..communication.protocol import Message

class CriticAgent(BaseAgent):
    def __init__(self, agent_id: str | None = None):
        super().__init__("Critic", agent_id)

    def evaluate_content(self, content: str, evaluation_criteria: List[str], thesis: str | None = None) -> Dict[str, Any]:
        print(f"Critic evaluating content based on: {evaluation_criteria}")
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        clarity = 3 if len(paragraphs) >= 3 else 2 if len(paragraphs) >= 2 else 1 if content.strip() else 0

        lower = content.lower()
        has_counter = any(token in lower for token in ["however", "but", "although", "counter", "然而", "但是", "不过", "反驳"])
        has_reasoning = any(token in lower for token in ["therefore", "thus", "because", "thereby", "因此", "所以", "说明", "表明"])
        thesis_anchor = bool(thesis and thesis.strip() and not thesis.startswith("[待填写") and thesis.strip().lower() in lower)

        argument_strength = 3 if has_reasoning and len(content) > 240 else 2 if has_reasoning or len(content) > 180 else 1 if content.strip() else 0
        counterargument = 3 if has_counter and "response" in lower else 2 if has_counter else 1 if content.strip() else 0
        evidence_grounding = 3 if content.count("Evidence from") >= 3 else 2 if "Evidence from" in content or "evidence" in lower else 1 if content.strip() else 0

        feedback_parts = []
        if not thesis_anchor and thesis and not thesis.startswith("[待填写"):
            feedback_parts.append("Draft does not yet anchor itself clearly to the thesis.")
        if not has_counter:
            feedback_parts.append("Counterargument handling is still weak.")
        if argument_strength <= 1:
            feedback_parts.append("Reasoning links between evidence and conclusion should be stronger.")
        if clarity <= 1:
            feedback_parts.append("Draft structure is still too thin.")
        if not feedback_parts:
            feedback_parts.append("Draft is structurally usable but still needs stronger evidence density.")

        return {
            "scores": {
                "clarity": clarity,
                "argument_strength": argument_strength,
                "counterargument": counterargument,
                "evidence_grounding": evidence_grounding,
                "thesis_alignment": 3 if thesis_anchor else 1 if thesis else 0,
            },
            "feedback": " ".join(feedback_parts),
        }

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
