from typing import List, Dict, Any
from .base import BaseAgent
from ..communication.protocol import Message

class ValidatorAgent(BaseAgent):
    def __init__(self, agent_id: str | None = None):
        super().__init__("Validator", agent_id)

    def validate_evidence(self, evidence_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"Validator validating {len(evidence_items)} evidence items")
        validation_results = {"validity_score": 0.0, "issues": []}
        # TODO: Implement logic to validate evidence: source reliability, claim alignment, etc.
        for i, item in enumerate(evidence_items):
            source = item.get('source')
            claim = item.get('claim')
            support = item.get('support')

            if not source or not claim or support is None:
                validation_results["issues"].append(f"Item {i}: Missing source, claim, or support.")
                continue

            # Simulate validation: Assume items with support > 0.7 are valid
            if support > 0.7:
                validation_results["validity_score"] += 1
            else:
                validation_results["issues"].append(f"Item {i}: Low support value ({support}) for claim '{claim[:30]}...'")

        if validation_results["validity_score"] == len(evidence_items):
            validation_results["validity_score"] = 1.0 # Perfect score if all valid
        else:
            validation_results["validity_score"] = validation_results["validity_score"] / len(evidence_items) if evidence_items else 0.0

        return validation_results

    def receive_message(self, message: Message):
        if "validate evidence" in message.content.lower():
            parts = message.content.split(":")
            if len(parts) > 1:
                evidence_str = parts[1].strip()
                try:
                    # This is highly unsafe and for demonstration only.
                    # In a real system, use proper serialization/deserialization.
                    evidence = eval(evidence_str)
                    if isinstance(evidence, list):
                        results = self.validate_evidence(evidence)
                        print(f"Validation results: {results}")
                    else:
                        print("Invalid evidence format.")
                except Exception as e:
                    print(f"Error processing evidence for validation: {e}")
            else:
                print("Invalid message format for validation.")

    def run(self, *args, **kwargs):
        print("Validator agent is ready. Waiting for evidence validation requests.")

    def stop(self):
        print(f"Stopping Validator ({self.agent_id[:6]}...)")
        super().stop()
