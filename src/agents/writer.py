from typing import List, Dict, Any
from .base import BaseAgent
from ..communication.protocol import Message
from ..knowledge_graph.graph_handler import KnowledgeGraphHandler

class WriterAgent(BaseAgent):
    def __init__(self, agent_id: str | None = None):
        super().__init__("Writer", agent_id)
        self.kg_handler = KnowledgeGraphHandler() # Placeholder
        self.current_paper_data: Dict[str, Any] = {}

    def draft_section(self, topic: str, evidence: List[Dict[str, Any]], thesis: str | None = None) -> str:
        print(f"Writer drafting section for topic: {topic}")
        intro = f"This section discusses {topic}."
        if thesis and thesis.strip() and not thesis.startswith("[待填写"):
            intro += f" It is written in service of the thesis: {thesis.strip()}"

        if not evidence:
            return (
                intro + " Current evidence is still limited, so this draft serves as a structural placeholder for later expansion."
            )

        lines = [intro]
        top_items = evidence[:3]
        for item in top_items:
            lines.append(f"Evidence from {item.get('source', 'unknown')} suggests that {item.get('claim', 'no claim')}.")
        if thesis and thesis.strip() and not thesis.startswith("[待填写"):
            lines.append("These points should be explicitly tied back to the thesis in the next revision.")
        else:
            lines.append("The section still needs a stronger thesis anchor and clearer causal links in a later iteration.")
        return "\n\n".join(lines)

    def integrate_with_paper(self, section_content: str):
        print("Writer integrating drafted section into paper...")
        # TODO: Implement logic to add drafted content to the paper.md file
        # For now, just print it
        print(section_content)

    def receive_message(self, message: Message):
        if "draft section" not in message.content.lower():
            return

        payload = message.metadata or {}
        topic = payload.get("topic")
        evidence = payload.get("evidence", [])
        thesis = payload.get("thesis")
        if not topic:
            print("Invalid message payload for drafting section.")
            return

        if not isinstance(evidence, list):
            print("Invalid evidence payload for drafting section.")
            return

        draft = self.draft_section(topic, evidence, thesis=thesis)
        self.integrate_with_paper(draft)

    def run(self, *args, **kwargs):
        print("Writer agent is ready. Waiting for drafting instructions.")

    def stop(self):
        print(f"Stopping Writer ({self.agent_id[:6]}...)")
        super().stop()
