# autowrite-academic

> Autonomous academic writing system with knowledge graph-guided evidence validation and structured iteration loops.

An implementation inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch) and [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill), designed to raise evidence quality rather than optimize for volume.

## Core Philosophy

**Graph first, then write. Evidence first, then claims. Thesis anchors everything.**

## Key Features

- **Multi-paper architecture**: Manage multiple papers without file collisions
- **Knowledge graph-guided evidence search**: Extract concepts, claims, evidence
- **6-dimensional quality rubric** (0-18 scale):
  - `evidence_grounding`: Claims with citations
  - `citation_validity`: Real & accurate sources
  - `argument_chain`: Premise → reasoning → conclusion
  - `counterargument`: Strongest opposing views
  - `clarity`: One point per paragraph
  - `graph_coherence`: Zero unsupported claims
- **Structured iteration loop**: Validation → diagnosis → strategy → search → edit → score
- **Incremental knowledge base**: Git-based tracking
- **Result tracking**: `results.tsv` logs all iterations

## Quick Start

```bash
# Create new paper
scripts/autowrite new my-topic --title "Research Question"

# Edit frontmatter (thesis, scope, audience)
vim papers/my-topic/paper.md

# Add source materials
cp ~/sources/*.md raw/
git add raw/ && git commit -m "docs: sources"

# Sync knowledge base
scripts/autowrite kb-sync

# Iterate until score reaches 16-18/18
scripts/autowrite status
cat papers/my-topic/results.tsv
```

## Project Structure

```
agents/                  # Protocol layer
  ├─ program.md         # 10-step iteration loop
  ├─ evidence_engine.md # Evidence validation
  └─ graph_engine.md    # Graph diagnostics

scripts/
  ├─ autowrite          # CLI tool
  └─ build_paper_graph.py

papers/
  ├─ .current           # Active paper
  └─ <slug>/
      ├─ paper.md       # Thesis + body
      ├─ paper_graph.json
      ├─ results.tsv    # Iteration log
      └─ graphify-out/

raw/                    # Source materials
```

## Quality Rubric (0-18)

- 0-6: draft
- 7-12: developing  
- 13-15: good
- 16-18: excellent (publication-ready)

## CLI Commands

```bash
scripts/autowrite new <slug> --title "..."
scripts/autowrite switch <slug>
scripts/autowrite status
scripts/autowrite list
scripts/autowrite validate
scripts/autowrite kb-sync
scripts/autowrite kb-sync --full
```

## Multi-Paper Workflow

Each paper is isolated in `papers/<slug>/` with its own:
- `paper.md` (thesis + body)
- `paper_graph.json` (knowledge graph)
- `results.tsv` (iteration history)

Active paper tracked in `papers/.current`.

## Incremental Knowledge Base

```bash
# Add to raw/ and commit
git add raw/ && git commit

# Sync (only changed files rescanned)
scripts/autowrite kb-sync
```

Uses git diff on `last_scan_commit` for incremental updates.

## Example Papers in Development

1. **governance-safety-security** (17/18, excellent)
   - Thesis: How correct performance assessment helps China avoid "Latin American trap"
   - Status: 2 iterations complete

2. **governance-modernization** (developing)
   - Thesis: Correct assessment drives Chinese modernization
   
3. **chinese-edu** (developing)
   - Thesis: Opportunities and challenges in international education

## Dependencies

- Python 3.7+ (stdlib only)
- Git
- vis.js (CDN)
- GitHub CLI (`gh`) optional

## Inspiration

- [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill)

## License

MIT

---

**Status:** Production-ready for single-author academic projects  
**Last Updated:** April 2026
