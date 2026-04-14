# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**autowrite v4** — autonomous academic writing system inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch) and [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill). Instead of lowering val_bpb, this agent raises evidence quality — guided by a knowledge graph and a thesis anchor.

Core philosophy: **Graph first, then write. Evidence first, then claims. Thesis anchors everything.**

## Project Structure

```
agents/                         # protocol layer — human-edited, agent read-only
  program.md                    # writing loop, 6×0–3 rubric, P0–P3 strategy library
  evidence_engine.md            # evidence search and validation rules
  graph_engine.md               # graph schema and diagnostics
raw/                            # shared corpus, git-tracked
papers/
  .current                      # one line: active paper slug
  <slug>/                       # one directory per paper — fully self-contained
    paper.md                    # YAML frontmatter (thesis/scope/...) + body — agent-edited
    paper_graph.json            # concept-argument-evidence graph, with _meta.last_scan_commit
    reader_prompts.md           # 3–5 adversarial reader questions for effect tests
    results.tsv                 # iteration log
    graphify-out/               # rendered graph.html + GRAPH_REPORT.md
scripts/
  autowrite                     # single CLI: new / switch / status / list / validate / kb-sync
  build_paper_graph.py          # graph scanner; supports --paper <slug> and --merge
```

## CLI

`scripts/autowrite` is the single entry point for paper-lifecycle operations:

```bash
scripts/autowrite new <slug> --title "..."   # scaffold papers/<slug>/
scripts/autowrite switch <slug>              # set active paper
scripts/autowrite status                     # show active paper + last 5 iterations
scripts/autowrite list                       # all papers
scripts/autowrite validate                   # integrity check (thesis/slug/graph/tsv)
scripts/autowrite kb-sync                    # incremental graph update from raw/
scripts/autowrite kb-sync --full             # force full rescan
```

Under `kb-sync`, raw/ must be committed (uncommitted changes block sync unless `--force`). The script uses `git diff` between `paper_graph.json._meta.last_scan_commit` and `HEAD` to scan only changed files, then merges into the existing graph via `build_paper_graph.py --merge`.

## How It Works

```
raw/ documents → autowrite kb-sync → papers/<slug>/paper_graph.json → structure
                                                                          ↓
                                      thesis check → diagnose (graph) → strategy (P0–P3)
                                                     ↓
                                      search evidence → edit paper.md → update graph
                                                     ↓
                                      score (6×0–3) → keep (commit) or discard (revert)
                                                     ↓
                                      every 3 keeps → reader-prompts effect test
                                                     ↓
                                      every 5 iterations → full graph rebuild + checkpoint
```

1. **Scaffold**: `autowrite new <slug>` creates the paper directory with empty templates.
2. **Anchor**: fill `thesis`, `scope_in`, `scope_out` in `papers/<slug>/paper.md` frontmatter. The thesis is the single source of truth — drift guard reads it every iteration.
3. **Build graph**: `autowrite kb-sync` scans `raw/` into `papers/<slug>/paper_graph.json`.
4. **Design structure from graph**: god nodes → sections, clusters → argument lines, gaps → research questions.
5. **Write loop**: follow `agents/program.md`. Each iteration targets the lowest-scoring rubric dimension and picks exactly one move from the strategy library.
6. **Rollback**: failed iterations are undone with `git revert` (never `reset --hard`), preserving the failure in history.
7. **Full graph rebuild** (`--scan papers/<slug>/paper.md --save-json`) every 5 iterations corrects drift.

## Multi-paper workflow

One repository, many papers, zero collision:

- Each paper lives in `papers/<slug>/` — fixed filenames (`paper.md`, `paper_graph.json`, ...) are namespaced by directory.
- `papers/.current` tracks which paper is active. Scripts default to the active paper unless `--paper <slug>` is passed.
- Switching: `autowrite switch <other>` — blocks if the current paper has uncommitted changes.
- Starting fresh: `autowrite new <new-slug>` and fill the frontmatter.
- Branch convention: each paper records its git branch in `paper.md` frontmatter (`branch_baseline`). `validate` warns if the current branch doesn't match.

## Incremental knowledge base

Add new documents to `raw/`, commit them, then say "update knowledge base" / run `autowrite kb-sync`. The sync:

1. Reads `_meta.last_scan_commit` from the active paper's `paper_graph.json`.
2. `git diff` against HEAD on `raw/` — only changed files are rescanned.
3. Merges results into the existing graph (replacing nodes whose `source_file` was rescanned).
4. Updates `_meta.last_scan_commit = HEAD`.
5. Logs a `kb_sync` row in `results.tsv`.

No custom hash index — git is the source of truth.

## Quality Rubric (6 × 0–3 = 0–18)

See `agents/program.md` for full level descriptions.

| Dimension | What it measures |
|---|---|
| `evidence_grounding` | % of factual claims with at least one `[@citation]` |
| `citation_validity` | Every cited source is real and says what we claim |
| `argument_chain` | Premise → reasoning → conclusion closed per section |
| `counterargument` | Core claims engage the strongest opposing view |
| `clarity` | One point per paragraph, no filler |
| `graph_coherence` | Zero unsupported claims, ≤ 1 disconnected cluster |

Composite score = sum (0–18). Each iteration targets the lowest dimension. Only strict score increases are kept.

## Graph Commands (direct)

```bash
# Render report from active paper's existing graph
python scripts/build_paper_graph.py

# Explicit slug (overrides .current)
python scripts/build_paper_graph.py --paper chinese-edu

# Full rescan of raw/ into active paper
python scripts/build_paper_graph.py --scan raw/ --save-json

# Full rebuild from paper.md (every 5 iterations)
python scripts/build_paper_graph.py --scan papers/chinese-edu/paper.md --save-json

# Merge mode (used internally by autowrite kb-sync)
python scripts/build_paper_graph.py --scan raw/ --save-json --merge
```

Zero external dependencies — Python stdlib only + vis.js CDN.

## Editing Considerations

- `agents/program.md`, `agents/evidence_engine.md`, `agents/graph_engine.md` are **human-controlled** — improve between sessions. The agent reads but must not edit them.
- `papers/<slug>/paper.md` and `paper_graph.json` are **agent-controlled** during a session — let the loop run.
- **Thesis is load-bearing** — never edit `paper.md` in a way that contradicts the frontmatter thesis. If the thesis itself needs to change, stop the loop and confirm with the user.
- All evidence must be real and verifiable. Hallucinated citations are the #1 failure mode.

## No Build/Test Commands

Quality is verified by the 6-dimension rubric in `agents/program.md`, the graph diagnostics in `GRAPH_REPORT.md`, and the reader-prompt effect test every 3 consecutive keeps.
