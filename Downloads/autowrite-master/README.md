# autowrite-academic

> Autonomous academic writing system with knowledge graph-guided evidence validation and structured iteration loops.

An implementation inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch) and [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill), designed to raise evidence quality rather than optimize for volume.

## Core Philosophy

**Graph first, then write. Evidence first, then claims. Thesis anchors everything.**

## Key Features

- **Multi-paper architecture**: Manage multiple papers in one repository without file collisions
- **Knowledge graph-guided evidence search**: Extract concepts, claims, and evidence from raw documents
- **6-dimensional quality rubric** (0-18 scale):
  - `evidence_grounding`: % of claims with citations
  - `citation_validity`: Sources are real and accurate
  - `argument_chain`: Premise → reasoning → conclusion
  - `counterargument`: Engaging strongest opposing views
  - `clarity`: One point per paragraph
  - `graph_coherence`: Zero unsupported claims
- **Structured iteration loop**: Thesis validation → diagnosis → strategy → search → edit → score → checkpoint
- **Incremental knowledge base**: Git-based tracking; only changed documents rescanned
- **Result tracking**: `results.tsv` logs iteration history with rubric scores

## Project Structure

```
agents/                          # Protocol layer (human-edited, agent read-only)
  ├─ program.md                 # 10-step iteration loop + P0-P3 strategy library
  ├─ evidence_engine.md         # Evidence search & validation rules
  └─ graph_engine.md            # Graph schema & diagnostics

scripts/                         # Core tools
  ├─ autowrite                  # CLI: new/switch/status/list/validate/kb-sync
  └─ build_paper_graph.py       # Knowledge graph scanner & renderer

papers/                          # Multi-paper workspace
  ├─ .current                    # Active paper slug (one line)
  └─ <slug>/
      ├─ paper.md               # YAML frontmatter + body (agent-edited)
      ├─ paper_graph.json        # Concept-argument-evidence graph
      ├─ reader_prompts.md       # 3-5 adversarial reader questions
      ├─ results.tsv             # Iteration log
      └─ graphify-out/
          ├─ graph.html          # Interactive visualization
          └─ GRAPH_REPORT.md     # Diagnostics

raw/                            # Shared corpus (git-tracked)
  └─ *.md                       # Source materials indexed by graph scanner
```

## CLI Usage

```bash
scripts/autowrite new <slug> --title "..."       # Scaffold new paper
scripts/autowrite switch <slug>                  # Activate paper
scripts/autowrite status                         # Current paper + last 5 iterations
scripts/autowrite list                           # All papers
scripts/autowrite validate                       # Thesis/scope/graph integrity check
scripts/autowrite kb-sync                        # Incremental graph update from raw/
scripts/autowrite kb-sync --full                 # Force full rescan
```

## Quality Rubric

| Dimension | What it measures | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| **evidence_grounding** | % claims with ≥1 citation | none | <50% | 50-90% | >90% |
| **citation_validity** | Sources real + say what claimed | hallucinated | ~25% | ~75% | all verified |
| **argument_chain** | Premise → reasoning → conclusion | disconnected | weak | mostly clear | closed per § |
| **counterargument** | Strongest opposing view addressed | none | weak version | fair but dismissed | integrated |
| **clarity** | One point/paragraph, no filler | rambling | meandering | mostly clear | tight |
| **graph_coherence** | Zero unsupported claims | many gaps | several clusters | ≤1 disconnected | unified |

**Total Score (0-18):**
- 0-6: draft
- 7-12: developing
- 13-15: good
- 16-18: excellent

## Multi-paper Workflow

Each paper is fully isolated in `papers/<slug>/` with its own:
- `paper.md` (thesis + body)
- `paper_graph.json` (knowledge graph)
- `reader_prompts.md` (effect tests)
- `results.tsv` (iteration log)

Active paper tracked in `papers/.current`. All scripts default to active paper unless `--paper <slug>` specified.

## Incremental Knowledge Base

```bash
# Add sources to raw/ and commit
cp ~/sources/*.md raw/
git add raw/ && git commit -m "docs: new materials"

# Sync knowledge graph (only changed files rescanned)
scripts/autowrite kb-sync
```

Uses git diff on `last_scan_commit` for incremental updates. No custom hashing.

## Example Workflow

```bash
# 1. Create paper
scripts/autowrite new my-topic --title "Research Question"

# 2. Fill frontmatter (thesis, scope, audience)
vim papers/my-topic/paper.md

# 3. Add raw materials and sync KB
cp ~/sources/*.md raw/
git add raw/ && git commit -m "docs: sources"
scripts/autowrite kb-sync

# 4. Iteration loop (repeat until score reaches 16-18)
#    - Research lowest rubric dimension
#    - Edit paper.md
#    - Score with rubric
#    - Commit if improved

# 5. Check progress
scripts/autowrite status
cat papers/my-topic/results.tsv
```

## Editing Guidelines

**Agent-controlled** (during session):
- `papers/<slug>/paper.md`
- `papers/<slug>/paper_graph.json`

**Human-controlled** (between sessions):
- `agents/program.md`
- `agents/evidence_engine.md`
- `agents/graph_engine.md`

**Load-bearing** (critical):
- Thesis in frontmatter—never contradict without stopping the loop
- All citations must be real and verifiable

## Dependencies

- Python 3.7+ (stdlib only)
- Git
- vis.js (CDN for graph visualization)
- GitHub CLI (`gh`) optional

## Inspiration

- [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill)
- Peer review standards + reproducibility criteria

## License

MIT

---

**Status:** Production-ready for single-author academic projects  
**Last Updated:** April 2026
