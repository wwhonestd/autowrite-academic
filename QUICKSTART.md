# Research OS v3 — Quick Start

## 1. Clone and start

```bash
git clone https://github.com/wwhonestd/autowrite.git my-paper
cd my-paper
```

## 2. (Optional) Add pre-collected documents

```bash
cp ~/path/to/papers/*.pdf raw/
cp ~/path/to/notes/*.md raw/
```

## 3. Start Claude Code and begin

```
Read agents/program.md and let's set up a new paper on [your topic].
```

For pre-collected documents, say:

```
Read agents/program.md. I have pre-collected documents in raw/. 
Please read them first, then set up a paper on [your topic].
```

For large document collections (>20 files), build graph first:

```
/graphify raw/
```

Then start the writing loop.

## 4. Let it run

The agent is fully autonomous. It will:
- Search for real evidence
- Write and revise the paper
- Build a knowledge graph every 3 iterations
- Score quality on 6 metrics
- Commit good changes, discard bad ones

Interrupt when satisfied or when the score plateaus.

## 5. Review results

```bash
cat results.tsv                          # iteration log
cat agents/paper.md                      # the paper
python scripts/build_paper_graph.py      # regenerate graph visualization
open graphify-out/graph.html             # interactive graph in browser
cat graphify-out/GRAPH_REPORT.md         # diagnostics report
git log --oneline                        # commit history
```

## File Ownership

| File | Who edits | Purpose |
|------|-----------|---------|
| `agents/program.md` | You | Writing loop rules |
| `agents/evidence_engine.md` | You | Evidence search strategy |
| `agents/graph_engine.md` | You | Graph construction protocol |
| `agents/paper.md` | Agent | The paper |
| `results.tsv` | Agent | Iteration log |
| `graphify-out/paper_graph.json` | Agent | Knowledge graph |
| `raw/*` | You | Pre-collected documents |
