# Graph Engine

The knowledge graph makes the paper's structure explicit and queryable. Uses `scripts/build_paper_graph.py` — zero external dependencies (Python stdlib + vis.js CDN).

## Principle

**The paper is a graph wearing a document costume.** Every claim depends on evidence, every concept connects to multiple claims. The graph makes these connections visible.

## Graph Schema

### Node Types

```
CONCEPT     — theoretical construct or analytical category
CLAIM       — specific assertion in the paper
EVIDENCE    — citable source with a specific finding
ACTOR       — named entity that acts in the analysis
SCENARIO    — defined future pathway or case
VARIABLE    — explanatory variable in the framework
```

### Edge Types

```
SUPPORTS        — evidence supports a claim (EVIDENCE → CLAIM)
CONTRADICTS     — opposes another node (EVIDENCE → CLAIM, CLAIM → CLAIM)
CITES           — claim references a source (CLAIM → EVIDENCE)
DEPENDS_ON      — claim requires another to hold (CLAIM → CLAIM)
OPERATIONALIZES — variable measures a concept (VARIABLE → CONCEPT)
PARTICIPATES_IN — actor relevant to a scenario (ACTOR → SCENARIO)
EXTENDS         — concept builds on another (CONCEPT → CONCEPT)
CONSTRAINS      — factor limits a scenario (VARIABLE → SCENARIO)
ANALOGOUS_TO    — structural similarity across domains
```

### Confidence Tags

Every edge carries a confidence tag:

```
EXTRACTED   — explicitly stated in source (confidence: 1.0)
INFERRED    — logically derivable but unstated (confidence: 0.6–0.9)
AMBIGUOUS   — plausible but uncertain (confidence: 0.1–0.5)
```

## JSON Format

Write to `graphify-out/paper_graph.json`:

```json
{
  "nodes": [
    {"id": "concept_escalation_ladder", "type": "CONCEPT", "label": "Escalation Ladder", "section": "2.1"}
  ],
  "edges": [
    {"source": "evidence_schelling1960", "target": "claim_limited_strikes", "relation": "SUPPORTS", "confidence": "EXTRACTED", "confidence_score": 1.0}
  ],
  "metadata": {
    "iteration": 12,
    "total_nodes": 47,
    "total_edges": 83
  }
}
```

Node ID convention: `{type_lowercase}_{short_name}` (e.g., `concept_proxy_war`, `evidence_bloom2015`).

## Commands

```bash
# Scan raw documents → build initial graph (BEFORE writing)
python scripts/build_paper_graph.py --scan raw/ --save-json

# Regenerate HTML + report from existing graph
python scripts/build_paper_graph.py

# Full rebuild from paper content (every 5 iterations)
python scripts/build_paper_graph.py --scan agents/paper.md --save-json
```

## Reading the Report

After running `build_paper_graph.py`, read `graphify-out/GRAPH_REPORT.md`. The diagnostic summary table:

| Check | Status | Priority |
|-------|--------|----------|
| Unsupported claims | FAIL/PASS | 1 — highest. A claim without evidence is the weakest point. |
| Uncontested claims | WARN/PASS | 2 — uncontested claims look like bias. |
| Orphan evidence | WARN/PASS | 3 — unused citations suggest incomplete integration. |
| God nodes | INFO | 4 — over-centralized concepts may mask thin reasoning. |
| Cross-community bridges | LOW/OK | 5 — structural coherence. Too few = fragmented argument. |

The first non-passing check becomes the target for the next writing iteration.

## Graph-Guided Evidence Search

The graph provides three search strategies for the evidence engine:

1. **Path-based discovery**: Two concepts in different communities but should connect → the gap suggests a search query.
2. **Evidence symmetry**: Scenario A has 5 evidence nodes, Scenario B (sharing variables) has 2 → search for Scenario B's gaps using A's evidence as seeds.
3. **Cluster surprise**: A node in an unexpected community signals a non-obvious connection worth investigating.

## Anti-Hallucination

- Every EVIDENCE node must have a verifiable `[@key]` in the References section.
- Every SUPPORTS edge must trace from a real source to a real claim.
- If a node exists in the graph but not in the paper, it is a ghost node — remove it.
- If the graph shows a citation supporting Claim X but the paper uses it for Claim Y, flag the inconsistency.
