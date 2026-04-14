from pathlib import Path
from typing import List, Dict, Any, Optional
from .base import BaseAgent
from ..communication.protocol import Message
from ..knowledge_graph.graph_handler import KnowledgeGraphHandler

class ResearcherAgent(BaseAgent):
    def __init__(self, agent_id: str | None = None):
        super().__init__("Researcher", agent_id)
        self.kg_handler = KnowledgeGraphHandler()
        self.current_research_topic: Optional[str] = None
        self.research_questions: List[str] = []

    def generate_research_questions(self, topic: str) -> List[str]:
        self.current_research_topic = topic
        print(f"Researcher generating questions for: {topic}")
        self.research_questions = [
            f"What are the key aspects of {topic}?",
            f"How does {topic} impact other areas?",
            f"What are the latest findings on {topic}?"
        ]
        return self.research_questions

    def retrieve_evidence(self, question: str, raw_dir: Optional[Path] = None, limit: int = 5) -> List[Dict[str, Any]]:
        print(f"Researcher retrieving evidence for: {question}")
        if raw_dir is None or not raw_dir.exists():
            return []

        keywords = [w.lower() for w in question.split() if len(w.strip()) >= 4]
        findings: List[Dict[str, Any]] = []

        fallback_findings: List[Dict[str, Any]] = []

        for path in sorted(raw_dir.glob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue

            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if lines:
                fallback_findings.append({
                    "source": f"raw/{path.name}",
                    "claim": lines[0][:300],
                    "support": 0.3,
                    "score": 0,
                })

            score = 0
            matched_line = None
            for line in lines:
                line_lower = line.lower()
                current = sum(1 for kw in keywords if kw in line_lower)
                if current > score:
                    score = current
                    matched_line = line

            if score > 0 and matched_line:
                findings.append({
                    "source": f"raw/{path.name}",
                    "claim": matched_line[:300],
                    "support": min(0.5 + score * 0.1, 0.95),
                    "score": score,
                })

        findings.sort(key=lambda x: x.get("score", 0), reverse=True)
        if findings:
            return findings[:limit]
        return fallback_findings[:limit]

    def integrate_into_kg(self, findings: List[Dict[str, Any]]):
        print("Researcher integrating findings into knowledge graph...")
        for idx, finding in enumerate(findings):
            self.kg_handler.add_node(f"evidence_{idx}", finding)

    def receive_message(self, message: Message):
        if "research topic" in message.content.lower():
            topic = message.content.split(":")[-1].strip()
            self.generate_research_questions(topic)
        elif "retrieve evidence for" in message.content.lower():
            question = message.content.split("for:")[-1].strip()
            findings = self.retrieve_evidence(question)
            self.integrate_into_kg(findings)

    def run(self, *args, **kwargs):
        if self.current_research_topic:
            print(f"Researcher continuing research on {self.current_research_topic}...")
            if self.research_questions:
                raw_dir = kwargs.get("raw_dir")
                for q in self.research_questions:
                    findings = self.retrieve_evidence(q, raw_dir=raw_dir)
                    self.integrate_into_kg(findings)
        else:
            print("Researcher is idle. Waiting for a research topic.")

    def stop(self):
        print(f"Stopping Researcher ({self.agent_id[:6]}...)")
        super().stop()
