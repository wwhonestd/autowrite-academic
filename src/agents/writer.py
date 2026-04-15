from typing import List, Dict, Any
from .base import BaseAgent
from ..communication.protocol import Message
from ..knowledge_graph.graph_handler import KnowledgeGraphHandler

class WriterAgent(BaseAgent):
    def __init__(self, agent_id: str | None = None):
        super().__init__("Writer", agent_id)
        self.kg_handler = KnowledgeGraphHandler() # Placeholder
        self.current_paper_data: Dict[str, Any] = {}

    def draft_section(self, topic: str, evidence: List[Dict[str, Any]]) -> str:
        print(f"Writer drafting section for topic: {topic}")
        if not evidence:
            return (
                f"This section discusses {topic}. "
                f"Current evidence is still limited, so this draft serves as a structural placeholder for later expansion."
            )

        lines = [f"This section discusses {topic}."]
        top_items = evidence[:3]
        for item in top_items:
            lines.append(f"Evidence from {item.get('source', 'unknown')} suggests that {item.get('claim', 'no claim')}.")
        lines.append("Taken together, these materials indicate that the argument should be expanded with stronger citations and clearer causal links in a later iteration.")
        return "\n\n".join(lines)

    def integrate_with_paper(self, section_content: str):
        print("Writer integrating drafted section into paper...")
        # TODO: Implement logic to add drafted content to the paper.md file
        # For now, just print it
        print(section_content)

    def receive_message(self, message: Message):
        if "draft section" in message.content.lower():
            parts = message.content.split(":")
            if len(parts) > 1:
                topic_and_evidence_str = parts[1].strip()
                # Very basic parsing: assume topic is before ';', evidence is a list of dicts string
                if '; ' in topic_and_evidence_str:
                    topic, evidence_str = topic_and_evidence_str.split('; ', 1)
                    try:
                        # This is highly unsafe and for demonstration only.
                        # In a real system, use proper serialization/deserialization.
                        evidence = eval(evidence_str)
                        if isinstance(evidence, list):
                            draft = self.draft_section(topic, evidence)
                            self.integrate_with_paper(draft)
                        else:
                            print("Invalid evidence format.")
                    except Exception as e:
                        print(f"Error processing evidence: {e}")
                else:
                    print("Invalid message format for drafting section.")
            else:
                print("Invalid message format for drafting section.")

    def run(self, *args, **kwargs):
        print("Writer agent is ready. Waiting for drafting instructions.")

    def stop(self):
        print(f"Stopping Writer ({self.agent_id[:6]}...)")
        super().stop()
