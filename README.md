# autowrite-academic

> Autonomous academic writing system with knowledge graph-guided evidence validation and structured iteration loops.

An implementation inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch) and [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill), designed to raise evidence quality rather than optimize for volume.

**Status:** Production-ready | **Current Version:** 1.0 | **Last Updated:** April 2026

---

## Table of Contents

- [Core Philosophy](#core-philosophy)
- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Complete Workflow](#complete-workflow)
- [Quality Rubric](#quality-rubric)
- [CLI Reference](#cli-reference)
- [Multi-Paper Management](#multi-paper-management)
- [Knowledge Base System](#knowledge-base-system)
- [Iteration Protocol](#iteration-protocol)
- [Example Papers](#example-papers)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Core Philosophy

**Graph first, then write. Evidence first, then claims. Thesis anchors everything.**

This system inverts the traditional academic writing approach:
- Instead of writing first, then searching for evidence: **Search first, validate evidence, then write**
- Instead of optimizing for volume or page count: **Optimize for quality and evidence grounding**
- Instead of isolated paper development: **Use knowledge graphs to connect concepts across papers**

## Key Features

- **Multi-paper architecture**: Manage multiple papers in one repository without file collisions
- **Knowledge graph-guided evidence search**: Extract concepts, claims, and evidence from raw documents using pattern analysis
- **6-dimensional quality rubric** (0-18 scale):
  - **evidence_grounding** (0-3): Percentage of claims with citations
  - **citation_validity** (0-3): Sources are real and say what we claim
  - **argument_chain** (0-3): Premise → reasoning → conclusion complete per section
  - **counterargument** (0-3): Strongest opposing views engaged & integrated
  - **clarity** (0-3): One point per paragraph, no filler
  - **graph_coherence** (0-3): Zero unsupported claims; unified graph
- **Structured iteration loop**: 10-step protocol with thesis validation, diagnosis, strategy selection, evidence search, editing, graph updates, scoring, and checkpointing
- **Incremental knowledge base**: Git-based differential tracking; only changed documents rescanned
- **Result tracking**: `results.tsv` logs all iterations with scores, dimensions, and notes
- **Interactive visualization**: Knowledge graphs rendered as interactive HTML with vis.js

---

## Installation

### Prerequisites

- Python 3.7 or higher
- Git
- Bash shell

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/wwhonestd/autowrite-academic.git
cd autowrite-academic

# 2. (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Verify installation
scripts/autowrite list
```

That's it! No pip install needed—all code uses Python stdlib and Git.

---

## Quick Start

### 1. Create a New Paper

```bash
scripts/autowrite new my-research --title "My Research Question"
```

This creates:
- `papers/my-research/paper.md` (frontmatter template + body)
- `papers/my-research/paper_graph.json` (empty graph)
- `papers/my-research/results.tsv` (iteration log)
- Updates `papers/.current` to track active paper

### 2. Fill the Frontmatter

Edit `papers/my-research/paper.md` and complete the YAML frontmatter:

```yaml
---
slug: my-research
title: My Research Question
thesis: "One or two sentences stating the core claim"
scope_in:
  - topic area 1
  - topic area 2
scope_out:
  - things NOT covered
  - out-of-scope items
audience: "Who should read this? (researcher types, practitioners, etc.)"
contribution: empirical  # or theoretical, methodological
branch_baseline: main
created_at: 2026-04-14
---
```

### 3. Add Source Materials

```bash
# Copy your research materials to raw/
cp ~/my-sources/*.md raw/
cp ~/papers/*.pdf raw/

# Commit them to git
git add raw/
git commit -m "docs: add source materials"
```

### 4. Build Knowledge Graph

```bash
scripts/autowrite kb-sync
```

This:
- Scans all files in `raw/` since last sync
- Extracts concepts, arguments, and evidence nodes
- Builds `papers/my-research/paper_graph.json`
- Generates `papers/my-research/graphify-out/graph.html` (interactive visualization)

### 5. Start Iterating

```bash
# View current status
scripts/autowrite status

# Edit your paper.md based on research findings
# Update the knowledge graph:
python scripts/build_paper_graph.py --paper my-research

# Check rubric scores in results.tsv
cat papers/my-research/results.tsv
```

### 6. Commit and Track Progress

```bash
# When you improve a rubric dimension:
git add papers/my-research/paper.md papers/my-research/paper_graph.json
git commit -m "iteration: add evidence for X dimension"

# Log result in results.tsv
# (Scripts do this automatically in the full workflow)
```

---

## Project Structure

```
.
├── README.md                          # This file
├── CLAUDE.md                          # Project documentation & guidelines
├── .gitignore                         # Git ignore rules
│
├── agents/                            # Protocol layer (human-edited)
│   ├── program.md                    # 10-step iteration loop + P0-P3 strategy library
│   ├── evidence_engine.md            # Evidence search & validation rules
│   └── graph_engine.md               # Graph schema & diagnostics
│
├── scripts/                           # Core tools
│   ├── autowrite                     # CLI: main entry point (executable)
│   └── build_paper_graph.py          # Knowledge graph scanner & HTML renderer
│
├── papers/                            # Multi-paper workspace
│   ├── .current                      # Single line: active paper slug
│   ├── <slug>/                       # One directory per paper
│   │   ├── paper.md                 # YAML frontmatter + markdown body (agent-edited)
│   │   ├── paper_graph.json         # Concept-argument-evidence graph (agent-edited)
│   │   ├── reader_prompts.md        # 3-5 adversarial reader questions
│   │   ├── results.tsv              # Iteration log with rubric scores
│   │   └── graphify-out/
│   │       ├── graph.html           # Interactive knowledge graph visualization
│   │       └── GRAPH_REPORT.md      # Graph diagnostics & statistics
│   └── <another-slug>/              # Multiple papers coexist with no collision
│
└── raw/                              # Shared corpus (git-tracked)
    ├── source1.md
    ├── source2.md
    └── ... (174+ documents for papers)
```

---

## Complete Workflow

```
[Initialize]
  ↓
new <slug> → Create papers/<slug>/ with templates
  ↓
[Prepare]
  ↓
Edit paper.md frontmatter (thesis, scope, audience)
  ↓
Add raw documents & commit
  ↓
kb-sync → Scan raw/ → Extract concepts/claims → Build graph
  ↓
[Iteration Loop (repeat until score 16-18)]
  ↓
1. THESIS CHECK
   └─ Verify no drift from frontmatter thesis

2. DIAGNOSE
   └─ Identify lowest-scoring rubric dimension

3. STRATEGY
   └─ Select one move from P0-P3 strategy library
      P0: Evidence (search, add citations)
      P1: Argument (strengthen logic, add counterarguments)
      P2: Structure (reorganize sections, improve flow)
      P3: Expression (refine language, clarity)

4. RESEARCH
   └─ Search raw/ documents for evidence

5. EDIT
   └─ Update paper.md with new content

6. GRAPH UPDATE
   └─ Regenerate paper_graph.json with build_paper_graph.py

7. SCORE
   └─ Rate each rubric dimension (0-3)
   └─ Calculate composite score (0-18)

8. DECIDE
   ├─ If score improved: KEEP (commit)
   └─ If score declined: DISCARD (git revert)

9. LOG
   └─ Add iteration row to results.tsv

10. CHECKPOINT
    └─ Every 5 iterations: full graph rebuild

[Test Every 3 Consecutive Keeps]
  ↓
reader_prompts.md → Run adversarial reader test
  └─ Verify paper holds up against criticism

[Monitor Progress]
  ↓
status → View last 5 iterations
list → Show all papers
validate → Check thesis/scope/graph integrity
```

---

## Quality Rubric

Each dimension is scored 0-3. Total composite score: 0-18.

### Dimensions

| Dimension | What it measures | 0 (failing) | 1 (weak) | 2 (good) | 3 (excellent) |
|-----------|------------------|-----------|---------|----------|---------------|
| **evidence_grounding** | % of claims with ≥1 citation | No citations | <50% | 50-90% | >90% cited |
| **citation_validity** | Sources are real + accurate | Hallucinated | ~25% accurate | ~75% accurate | All verified |
| **argument_chain** | Premise → reasoning → conclusion | Disconnected | Weak links | Mostly clear | Closed per § |
| **counterargument** | Strongest opposing view engaged | None | Weak version | Fair but dismissed | Fully integrated |
| **clarity** | One point per paragraph | Rambling | Meandering | Mostly clear | Tight, focused |
| **graph_coherence** | Zero unsupported claims | Many gaps | Several clusters | ≤1 disconnected | Unified graph |

### Grade Ranges

- **0-6/18:** Draft (needs major work)
- **7-12/18:** Developing (coherent but gaps remain)
- **13-15/18:** Good (ready for peer review)
- **16-18/18:** Excellent (publication-ready)

---

## CLI Reference

### `scripts/autowrite new <slug> [--title "..."]`

Create a new paper.

```bash
scripts/autowrite new governance-analysis --title "How Policy Design Affects Outcomes"
```

Options:
- `--title`: Paper title (optional, can edit later)

Creates:
- `papers/governance-analysis/` with templates
- Updates `papers/.current` to `governance-analysis`

---

### `scripts/autowrite switch <slug>`

Switch active paper. Requires clean git state (commit or stash changes first).

```bash
scripts/autowrite switch chinese-education
```

---

### `scripts/autowrite status`

Show active paper and last 5 iterations.

```bash
scripts/autowrite status
```

Output:
```
Active paper: governance-safety-security
Branch: autowrite/governance-modernization

Last 5 iterations:
  0   baseline         12/18   evidence, citation, coherence
  1   22475f5          15/18   ↑ evidence, citation, coherence
  2   73bf776          17/18   ↑ citation, counterargument
  -   (next iteration)
```

---

### `scripts/autowrite list`

List all papers with their current scores.

```bash
scripts/autowrite list
```

---

### `scripts/autowrite validate`

Check paper integrity: thesis, scope, graph connectivity.

```bash
scripts/autowrite validate
```

Warns about:
- Missing thesis or scope fields
- Branch name mismatch
- Disconnected graph nodes

---

### `scripts/autowrite kb-sync [--full] [--force]`

Synchronize knowledge base from `raw/` documents.

```bash
# Incremental sync (default)
scripts/autowrite kb-sync

# Full rescan (force rebuild)
scripts/autowrite kb-sync --full

# Sync without uncommitted file check
scripts/autowrite kb-sync --force
```

Behind the scenes:
1. Reads `_meta.last_scan_commit` from `paper_graph.json`
2. Runs `git diff` on `raw/` between that commit and HEAD
3. Rescans only changed files
4. Merges into existing graph (preserves old nodes)
5. Updates `_meta.last_scan_commit = HEAD`
6. Logs result in `results.tsv`

---

## Multi-Paper Management

### How It Works

One repository, many papers, **zero collision:**

- Each paper lives in `papers/<slug>/` with fixed filenames
- `papers/.current` tracks which paper is active
- All scripts default to active paper (override with `--paper <slug>`)
- Papers can be on different git branches

### Switching Papers

```bash
# Before switching, commit any changes
git add papers/governance-safety-security/
git commit -m "iteration: improved evidence section"

# Switch
scripts/autowrite switch chinese-education

# You're now working on papers/chinese-education/
```

### Working on Multiple Papers

```bash
# Commit all changes in current paper
git add papers/*/
git commit -m "completed iteration on all papers"

# Switch to different paper
scripts/autowrite switch my-other-topic

# Make changes
# ... edit paper.md ...

# Commit
git add papers/my-other-topic/
git commit -m "..."

# Switch back
scripts/autowrite switch original-topic
```

---

## Knowledge Base System

### Graph Structure

The knowledge graph (`paper_graph.json`) contains three types of nodes:

```json
{
  "nodes": [
    {
      "id": "concept_GDP",
      "label": "GDP",
      "type": "concept",
      "definition": "Gross Domestic Product",
      "source_file": "raw/02-latin-american-trap.md"
    },
    {
      "id": "claim_gdp_growth",
      "label": "GDP growth alone doesn't prevent crises",
      "type": "claim",
      "support": 2,
      "evidence_count": 3,
      "source_file": "raw/02-latin-american-trap.md"
    },
    {
      "id": "evidence_chile",
      "label": "Chile investment fell from 9.3% to 0.2%",
      "type": "evidence",
      "source_file": "raw/02-latin-american-trap.md",
      "citations": ["@chile_lost_decade"]
    }
  ],
  "edges": [
    { "from": "claim_gdp_growth", "to": "concept_GDP" },
    { "from": "claim_gdp_growth", "to": "evidence_chile" }
  ],
  "_meta": {
    "last_scan_commit": "abc123...",
    "nodes_total": 44,
    "edges_total": 45
  }
}
```

### Incremental Sync Algorithm

1. **Read baseline**: `last_scan_commit` from `_meta`
2. **Identify changed files**: `git diff <commit> HEAD -- raw/`
3. **Rescan changed files**: Extract new concepts, claims, evidence
4. **Merge with old graph**:
   - Delete nodes where `source_file` was rescanned
   - Keep nodes from unmodified files
   - Add new nodes
   - Recompute edges
5. **Update baseline**: `last_scan_commit = HEAD`
6. **Render visualization**: `graph.html` + `GRAPH_REPORT.md`

**Why this works:** Git is the source of truth. No custom hash indexing. Deterministic.

---

## Iteration Protocol

See `agents/program.md` for the full 10-step loop and P0-P3 strategy library.

### P0: Evidence (Fastest)
- Add more citations
- Extract specific data from raw documents
- Build comparison tables
- Add quantitative examples

### P1: Argument (Medium)
- Add counterargument voices
- Strengthen premise-conclusion connections
- Integrate opposing views
- Improve logical flow

### P2: Structure (Medium)
- Reorganize sections for better flow
- Add missing transitions
- Clarify argument hierarchy
- Improve section connections to thesis

### P3: Expression (Slowest)
- Refine language and clarity
- Remove filler sentences
- Improve readability
- Polish for publication

---

## Example Papers

### 1. governance-safety-security (17/18 - Excellent)

**Thesis:** How correct performance assessment helps China avoid the "Latin American trap" by decoupling development from political instability.

**Status:** 2 iterations complete
- Iteration 0: 12/18 (baseline outline)
- Iteration 1: 15/18 (+evidence from Latin America cases)
- Iteration 2: 17/18 (+counterargument on democracy & state capacity)

**Key sections:**
- §2: Literature review with Latin American case studies
- §5: Three findings (evaluation system, incentive mechanism, risk prevention)
- §6: Discussion addressing democratic accountability objections

**Branch:** `autowrite/governance-modernization`

### 2. governance-modernization (Developing)

**Thesis:** Correct performance assessment drives multiple dimensions of Chinese modernization (economic quality, environmental protection, public services equity).

**Status:** Baseline outline (12/18)
**Branch:** `autowrite/governance-modernization`

### 3. chinese-international-education (Developing)

**Thesis:** China's international education must shift from English-America centric models to diversified pathways via Belt & Road and co-hosted institutions.

**Status:** Placeholder (needs content)
**Branch:** `autowrite/chinese-international-education-opportunities-challenges`

---

## Dependencies

### Core
- **Python 3.7+** (stdlib only: `json`, `re`, `pathlib`, `subprocess`, `argparse`)
- **Git** (for version control and diff-based incremental updates)
- **Bash** (for CLI scripts)

### Optional
- **vis.js** (CDN-loaded; for interactive graph visualization in HTML output)
- **GitHub CLI** (`gh`) for remote repository operations
- **Your favorite editor** (vim, VS Code, etc.) for paper.md

### Zero external Python dependencies!

All graph processing, pattern extraction, and rendering uses Python stdlib.

---

## Troubleshooting

### Issue: "cannot switch papers—uncommitted changes"

**Solution:** Commit your changes first.

```bash
git add papers/current-paper/
git commit -m "iteration: improvements"
scripts/autowrite switch another-paper
```

### Issue: Knowledge graph not updating

**Solution:** Make sure raw/ files are committed.

```bash
git status raw/
# If modified, commit them:
git add raw/
git commit -m "docs: update sources"

# Then sync:
scripts/autowrite kb-sync
```

### Issue: "results.tsv" has odd formatting

**Solution:** It's a TSV (tab-separated). Open in Excel, Numbers, or `column -t -s $'\t'`:

```bash
column -t -s $'\t' papers/my-topic/results.tsv
```

### Issue: Graph visualization (graph.html) is blank

**Solution:** 
1. Check that knowledge graph has nodes: `cat papers/my-topic/paper_graph.json | grep "nodes"`
2. Regenerate: `python scripts/build_paper_graph.py --paper my-topic`
3. Open in browser: `open papers/my-topic/graphify-out/graph.html`

### Issue: CLI commands not found

**Solution:** Make sure scripts are executable and in PATH.

```bash
chmod +x scripts/autowrite
# Run with explicit path:
./scripts/autowrite list
# Or add to PATH:
export PATH="$PATH:$(pwd)/scripts"
autowrite list
```

---

## Contributing

This is a single-author research tool, not a collaborative framework. However:

- **Fork & adapt:** Customize for your own papers
- **Report bugs:** Create GitHub issues
- **Propose improvements:** Fork and create pull requests
- **Cite:** If you build on this work, cite the GitHub repo

---

## License

MIT License. See LICENSE file for details.

---

## Citation

If you use this system in your research, cite as:

```bibtex
@software{autowrite_academic,
  title={autowrite-academic: Autonomous Academic Writing with Knowledge Graphs},
  author={wwhonestd},
  year={2026},
  url={https://github.com/wwhonestd/autowrite-academic}
}
```

---

## Acknowledgments

- Inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- Framework influenced by [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill)
- Built with [Claude Code](https://claude.ai/code)

---

## Support

For questions or issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review `CLAUDE.md` for project guidelines
3. Read `agents/program.md` for iteration protocol
4. Open a GitHub issue

---

**Happy writing! 🚀**

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
