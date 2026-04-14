# autowrite v4 — writing loop protocol

Graph first, then write. Evidence first, then claims.
Thesis is the anchor — every edit must serve it, or it is discarded.

This file is **human-controlled** — the agent reads it each session but never edits it.
All writing happens inside `papers/<slug>/paper.md`, where `<slug>` is the line in `papers/.current`.

## Setup (per paper)

1. **Create**: `scripts/autowrite new <slug> --title "..."` — scaffolds `papers/<slug>/`.
2. **Edit frontmatter**: open `papers/<slug>/paper.md` and fill `thesis`, `scope_in`, `scope_out`, `audience`. The `thesis` field is load-bearing — do not leave the placeholder.
3. **Activate**: `scripts/autowrite switch <slug>`.
4. **Build initial graph**: `scripts/autowrite kb-sync` (scans `raw/`, writes `papers/<slug>/paper_graph.json`).
5. **Validate**: `scripts/autowrite validate` — must exit clean before entering the loop.
6. **Baseline**: score the skeleton on the rubric below, log iter 0 to `results.tsv`, confirm with user.

## The Loop

Every iteration runs these steps in order. Do not skip step 0.

0. **Thesis check** — read the frontmatter of `papers/<slug>/paper.md`. Hold `thesis` and `scope_in` in working memory for this iteration. Any edit that does not serve the thesis or crosses `scope_out` is automatically discarded in step 7.

1. **Diagnose** — run `python scripts/build_paper_graph.py` (or `--scan papers/<slug>/paper.md --save-json` on rebuild iterations). Read the Diagnostic Summary in `GRAPH_REPORT.md`. The **lowest-scoring rubric dimension** is this iteration's target. Tie-break by priority: P0 > P1 > P2 > P3.

2. **Strategy** — pick exactly one move from the strategy library matching the target dimension. One move per iteration: multiple simultaneous changes break attribution.

3. **Research** — if the move needs new evidence, follow `evidence_engine.md`. Use graph-guided discovery (path queries, evidence symmetry, cluster surprises). Never fabricate.

4. **Edit** — one focused change to `papers/<slug>/paper.md`. Do not rewrite the whole paper.

5. **Update graph** — edit `papers/<slug>/paper_graph.json` to reflect the change. Run `python scripts/build_paper_graph.py --paper <slug>` to regenerate the report. Full rebuild (`--scan papers/<slug>/paper.md --save-json`) every 5 iterations.

6. **Score** — run the 6-dimension rubric below. Composite = sum of dimension scores (0–18).

7. **Decide** —
   - Composite strictly **greater** than previous iteration AND thesis/scope respected → `git commit`.
   - Composite **equal or lower**, or thesis/scope violated → `git revert HEAD` (never `git reset --hard`).

8. **Log** — append one row to `papers/<slug>/results.tsv` (schema at bottom).

9. **Checkpoint** — every 5 iterations or at the end of a section, stop and show the user: diff, score delta, which dimension moved, failed attempts. Await confirmation before continuing.

10. **Repeat**.

## Rubric (6 dimensions × 0–3 = 0–18)

Score each dimension 0, 1, 2, or 3. Composite is the raw sum. Target the lowest score each round.

| # | Dimension | 0 (fail) | 1 (weak) | 2 (ok) | 3 (strong) |
|---|---|---|---|---|---|
| 1 | `evidence_grounding` | >20% claims uncited | 5–20% uncited | <5% uncited | every claim cited |
| 2 | `citation_validity` | fabricated citations present | 1–2 suspect | all real but some weak links | all real and strong |
| 3 | `argument_chain` | multiple broken chains | local gaps | mostly closed | premise→reason→conclusion closed per section |
| 4 | `counterargument` | none | mentioned, not addressed | addressed in ≥1 core claim | systematic across core claims |
| 5 | `clarity` | bloated, off-topic, filler-heavy | redundant | clear | one point per paragraph, zero filler |
| 6 | `graph_coherence` | many orphans + unsupported | >1 cluster gap | ≤1 cluster gap | fully connected, zero unsupported |

## Strategy Library (priority-ordered — pick one per iteration)

### P0 — Evidence layer
Triggered when `evidence_grounding` or `citation_validity` is the lowest dimension.
- Cross-reference `GRAPH_REPORT.md` orphan-evidence and unsupported-claim lists to locate the exact target.
- For each unsupported claim: either add a real citation or delete the claim. No middle ground.
- Replace weak secondary citations with primary sources — search per `evidence_engine.md`.

### P1 — Argument layer
Triggered when `argument_chain` or `counterargument` is the lowest.
- Rewrite the broken causal chain in the flagged section, making premise → reasoning → conclusion explicit.
- For each core claim, proactively find the strongest opposing view and engage it, not a straw man.
- Mark counterarguments in the graph with `CONTRADICTS` edges so future diagnostics can see the balance.

### P2 — Structure layer
Triggered when `graph_coherence` is the lowest.
- Merge or split clusters; add bridging paragraphs between disconnected communities.
- Promote a high-degree god-node concept to a section anchor or subsection title.
- Prune orphan nodes that have no route back to a section.

### P3 — Expression layer
Triggered when `clarity` is the lowest.
- One point per paragraph. Split paragraphs that carry two ideas.
- Delete filler, nominalizations, and hedges that do not carry semantic load.
- Tighten topic sentences until each one could stand alone as an entry in an outline.

## Effect Test (every 3 consecutive keeps)

After 3 consecutive `keep` iterations, run the reader-prompt test:

1. Spawn an independent sub-agent with `papers/<slug>/reader_prompts.md`.
2. The sub-agent answers each prompt using only the current `paper.md`.
3. Rate each answer 0–3: does the paper actually defend against the prompt?
4. Average across prompts; log as a row in `results.tsv` with `eval_mode=full_test`.
5. If the average drops vs the previous test, force next iteration to use P1 (argument layer).

When a sub-agent is unavailable, perform a `dry_run`: read the prompts and mentally walk the paper. Log with `eval_mode=dry_run`. Dry-runs are strictly inferior to full tests but better than skipping.

## Exploratory Rewrite (anti-stall)

After **3 consecutive discards**, propose an exploratory rewrite of the flagged section to the user. Execute only with explicit confirmation. Procedure:

1. `git stash` the current version of the section.
2. Rewrite the section from the graph structure, not by editing the old text.
3. Re-score.
4. If the rewrite's composite > stashed: keep; else `git stash pop` and return to normal loop.

## Rules

**CAN**: edit `papers/<slug>/paper.md`, `papers/<slug>/paper_graph.json`, `papers/<slug>/results.tsv`. Run `scripts/autowrite` and `scripts/build_paper_graph.py`. Search for evidence per `evidence_engine.md`.

**CANNOT**: fabricate citations; modify `agents/*.md` (human-owned protocol layer); skip the thesis check; use `git reset --hard` (always `revert`); add graph nodes without corresponding paper content (except during `kb-sync` of `raw/`).

## `results.tsv` schema

Tab-separated, one row per iteration or kb_sync event:

```
iteration  commit    old_score  new_score  dimension            status    eval_mode  note
0          baseline  -          5          -                    baseline  dry_run    initial skeleton
1          a1b2c3d   5          7          evidence_grounding   keep      dry_run    added 3 citations to §2.1
2          b2c3d4e   7          6          clarity              revert    dry_run    overtrimmed intro
3          c3d4e5f   7          9          argument_chain       keep      dry_run    closed §3 causal chain
4          -         -          -          -                    kb_sync   -          +2 files merged from raw/
```

- `status`: `keep` | `revert` | `baseline` | `kb_sync`
- `dimension`: the rubric dimension targeted this iteration (or `-` for non-iteration rows)
- `eval_mode`: `full_test` (sub-agent ran reader prompts) | `dry_run` (structural-only) | `-`

## Simplicity criterion

Between two versions with equal composite scores, the one with fewer words wins. Keep the shorter.

## Never stop until

5 consecutive discards AND user confirms stop. Otherwise: re-read for overlooked weaknesses, search newer literature, propose an exploratory rewrite.
