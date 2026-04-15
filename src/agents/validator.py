from typing import List, Dict, Any
from .base import BaseAgent
from ..communication.protocol import Message

class ValidatorAgent(BaseAgent):
    def __init__(self, agent_id: str | None = None):
        super().__init__("Validator", agent_id)

    def validate_evidence(self, evidence_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"Validator validating {len(evidence_items)} evidence items")
        validation_results = {"validity_score": 0.0, "issues": []}
        if not evidence_items:
            validation_results["issues"].append("No evidence items were available for validation.")
            return validation_results

        valid_count = 0
        for i, item in enumerate(evidence_items):
            source = item.get('source')
            claim = item.get('claim')
            support = item.get('support')

            if not source or not claim or support is None:
                validation_results["issues"].append(f"Item {i}: Missing source, claim, or support.")
                continue

            if support >= 0.75:
                valid_count += 1
            elif support >= 0.5:
                validation_results["issues"].append(f"Item {i}: Medium support value ({support}) for claim '{claim[:30]}...'")
            else:
                validation_results["issues"].append(f"Item {i}: Low support value ({support}) for claim '{claim[:30]}...'")

        validation_results["validity_score"] = valid_count / len(evidence_items)
        return validation_results

    def receive_message(self, message: Message):
        if "validate evidence" not in message.content.lower():
            return

        payload = message.metadata or {}
        evidence = payload.get("evidence", [])
        if not isinstance(evidence, list):
            print("Invalid evidence payload for validation.")
            return
        results = self.validate_evidence(evidence)
        print(f"Validation results: {results}")

    def run(self, *args, **kwargs):
        print("Validator agent is ready. Waiting for evidence validation requests.")

    def stop(self):
        print(f"Stopping Validator ({self.agent_id[:6]}...)")
        super().stop()
