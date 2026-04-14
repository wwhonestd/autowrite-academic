from typing import List, Dict, Any, Optional
from src.agents.base import BaseAgent
from src.communication.protocol import Message
from src.knowledge_graph.graph_handler import KnowledgeGraphHandler # Assuming this will be created later

class WriterAgent(BaseAgent):
    def __init__(self, agent_id: str | None = None):
        super().__init__("Writer", agent_id)
        self.kg_handler = KnowledgeGraphHandler() # Placeholder
        self.current_paper_data: Dict[str, Any] = {}

    def draft_section(self, topic: str, evidence: List[Dict[str, Any]]) -> str:
        print(f"Writer drafting section for topic: {topic}")
        # TODO: Implement LLM-based writing to draft a section using evidence
        draft = f"This section discusses {topic}. Based on the provided evidence:\n"
        for item in evidence:
            draft += f"- From {item.get('source', 'unknown')}: {item.get('claim', 'no claim')}\n"
        return draft

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
