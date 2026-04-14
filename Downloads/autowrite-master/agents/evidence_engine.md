# Evidence Engine

The evidence engine is the core differentiator of autowrite. Without it, the agent produces plausible-sounding text. With it, the agent produces papers with real, verifiable foundations.

## Principle

**Never write a claim, then look for evidence. Always find evidence, then decide what to claim.**

This inverts the typical AI writing flow. Most systems generate text first and "add citations" as decoration. This system searches first and writes from what it finds.

## Evidence Hierarchy

Not all evidence is equal. When building arguments, prefer higher-tier evidence:

```
Tier 1 — Systematic reviews, meta-analyses, large-scale replicated studies
Tier 2 — Peer-reviewed empirical studies (RCT, longitudinal, large-N observational)
Tier 3 — Peer-reviewed theoretical/conceptual papers, well-cited working papers
Tier 4 — Conference proceedings, institutional reports, government data
Tier 5 — Books, dissertations, credible news sources
Tier 6 — Blog posts, preprints, opinion pieces (use sparingly, flag as weak)
```

A claim supported only by Tier 5–6 evidence should be explicitly marked as tentative.

## Two Evidence Sources

### Source A: Local Materials (`raw/`)

Pre-collected documents the user provides. These are the primary source — already curated, likely high quality. Scan them first via `python scripts/build_paper_graph.py --scan raw/ --save-json`.

### Source B: Online Search

When the graph diagnoses gaps (unsupported claims, missing counter-evidence, thin clusters), search online to fill them. This is the supplement — use it when `raw/` is insufficient.

## Search Protocol

### Step 1: Formulate search queries

Generate 3–5 queries from different angles:

- **Direct**: the claim itself as a search query
- **Theoretical**: the underlying theory or framework
- **Empirical**: "study" or "experiment" + the phenomenon
- **Opposing**: "critique of" or "limitations of" + the claim
- **Recent**: add year filters for the latest work

Use graph-guided strategies alongside standard queries: path-based discovery for cross-domain connections, evidence symmetry for gap-filling, cluster-surprise for non-obvious links (see Graph-Guided Discovery below).

### Step 2: Execute searches

Use tools in this priority order:

1. **Exa Search** (`mcp__exa__web_search_exa`) — semantic search, best for finding academic papers and research reports. Use natural language queries like "empirical study on remote work productivity gains" rather than keywords. Set `includeDomains` to `["scholar.google.com", "semanticscholar.org", "arxiv.org", "jstor.org", "ncbi.nlm.nih.gov"]` for academic-focused results.
2. **WebSearch** — general web search, good for government reports, institutional data, policy documents, and news sources.
3. **Exa Crawl** (`mcp__exa__crawling_exa`) — read full content from a specific URL. Use after finding a promising result in step 1/2 to extract the actual content.
4. **WebFetch** — fetch and analyze a specific URL. Use to verify a source exists and says what we think it says.

For each search result, extract:

- Paper title, authors, year, venue
- Key finding relevant to our claim
- Sample size / methodology (for empirical work)
- Direct quotes if critical

### Step 3: Judge source quality

Every search result must pass this 5-point quality gate before it can be cited:

| Check | Question | Fail action |
|-------|----------|-------------|
| **Existence** | Can I access the actual content (abstract, full text, or summary)? | Discard — never cite a title-only result |
| **Authorship** | Are the authors identifiable? Is it published in a known venue? | Downgrade to Tier 5–6 or discard |
| **Relevance** | Does it directly address our claim, or is the connection a stretch? | Discard if tangential |
| **Recency** | Is it current enough for the claim? (policy: ≤5 years; theory: ≤15 years) | Flag as dated if old |
| **Consistency** | Does the finding align with or meaningfully contradict other evidence we have? | If isolated outlier with weak methodology, discard |

**Quality scoring shortcut**: A source that passes all 5 checks AND has identifiable peer-review status = Tier 1–4. A source missing peer-review but passing others = Tier 5. A source failing any check = discard or Tier 6 with explicit caveat.

### Step 4: Save to `raw/`

When a search yields high-quality material, save it to `raw/` so it enters the knowledge graph:

```markdown
# raw/searched_[topic]_[date].md

## Source: [Full citation]
## URL: [source URL]
## Tier: [1-6]
## Retrieved: [date]

[Key findings, quotes, data extracted from the source]
```

This ensures searched materials are integrated into the graph on the next rebuild, not just cited in passing.

### Step 5: Validate before citing

Before citing anything, verify:

- [ ] The paper/source actually exists (confirmed via Exa Crawl or WebFetch)
- [ ] The finding we attribute to it is what it actually says (read the content, not just the title)
- [ ] The methodology is sound enough to support the weight of our claim
- [ ] The source is not retracted or widely disputed

If validation fails, discard the source. Do NOT cite it.

### Step 6: Build the evidence chain

For each argument in the paper, construct:

```
CLAIM: [what we assert]
├── EVIDENCE 1: [source] found [finding] using [method] with [N subjects]
├── EVIDENCE 2: [source] replicated/extended this by showing [finding]
├── COUNTEREVIDENCE: [source] argues [opposing view] because [reason]
└── SYNTHESIS: Despite [counterevidence], the weight of evidence supports [claim] because [reasoning]
```

## Citation Format

Use Markdown reference-style citations:

```markdown
Remote work increases individual productivity by 13% on average [@bloom2015working],
though this effect diminishes for collaborative tasks [@yang2022effects].
```

At the bottom of `paper.md`, maintain a references section:

```markdown
## References

[@bloom2015working]: Bloom, N., Liang, J., Roberts, J., & Ying, Z. J. (2015).
Does working from home work? Evidence from a Chinese experiment.
*Quarterly Journal of Economics*, 130(1), 165-218.
```

## Handling Evidence Gaps

When you cannot find sufficient evidence for a claim:

1. **Acknowledge explicitly**: "To the best of our knowledge, no empirical study has directly tested this relationship."
2. **Provide indirect evidence**: "Related work on [adjacent topic] suggests [indirect finding]."
3. **Flag for future research**: Add to the "Future Research" section.
4. **Consider removing the claim**: If it cannot be supported at all, the paper is better without it.

Never fill an evidence gap with vague language like "research has shown" or "studies suggest" without a specific citation.

## Anti-Hallucination Safeguards

The single biggest risk in AI-assisted writing is fabricated citations. Defenses:

1. **Search-first workflow**: Find the paper before writing the claim, not after.
2. **Read-before-cite**: Never cite a source you haven't read at least the abstract of (via Exa Crawl or WebFetch).
3. **Cross-validation**: For critical claims, find the same finding reported by ≥2 independent sources.
4. **Uncertainty markers**: Use `[citation needed]` or `[evidence pending]` rather than making up a reference.
5. **Audit trail**: Each evidence search is saved to `raw/` so the human can verify.

## Graph-Guided Discovery

When the paper graph exists, the evidence engine gains three additional search strategies:

### Strategy 1: Path-Based Query Generation

If two concepts are in different graph communities but should be connected, the gap suggests a search query. Example: "proxy warfare" and "energy markets" in separate communities → search for "proxy conflict economic impact."

### Strategy 2: Evidence Symmetry Check

If Scenario A has 5 supporting evidence nodes but Scenario B (sharing variables with A) has only 2, the gap in Scenario B is a priority search target. Use Scenario A's evidence as analogical search seeds.

### Strategy 3: Cluster-Surprise Investigation

If a node lands in an unexpected community (e.g., an ACTOR node among CONCEPT nodes), this signals a non-obvious connection. Search for literature that explains or validates it.

## Evidence Density Targets

| Section | Target | Rationale |
|---------|--------|-----------|
| Introduction | 3–5 citations per paragraph | Establishes the problem is real and recognized |
| Literature Review | 5–8 citations per paragraph | This IS the evidence section |
| Theoretical Framework | 2–4 citations per paragraph | Grounding in established theory |
| Methodology | 1–3 citations per paragraph | Justifying method choices |
| Results | 0–1 citations per paragraph | Your own findings speak here |
| Discussion | 3–6 citations per paragraph | Connecting findings back to literature |
| Conclusion | 1–2 citations per paragraph | Summarizing, not introducing new evidence |

Sections falling below these targets are automatically flagged as weak points in the writing loop.
