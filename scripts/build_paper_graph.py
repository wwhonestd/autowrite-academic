#!/usr/bin/env python3
"""Paper knowledge graph builder — two modes:

Mode 1 (default): Read paper_graph.json → HTML + report
Mode 2 (--scan):  Scan raw/ documents → extract graph → HTML + report

Adapted from ObsidianWiki/scripts/build_graph.py for academic paper analysis.
Zero external dependencies — uses only Python standard library + vis.js CDN.

Usage:
    python scripts/build_paper_graph.py                          # from paper_graph.json
    python scripts/build_paper_graph.py --scan                   # scan raw/ + agents/paper.md
    python scripts/build_paper_graph.py --scan raw/              # scan specific directory
    python scripts/build_paper_graph.py --scan raw/ agents/      # scan multiple directories
    python scripts/build_paper_graph.py --input graph.json       # custom JSON input
    python scripts/build_paper_graph.py --html-only              # skip report
"""

import json
import re
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAPERS_DIR = PROJECT_ROOT / "papers"


def _paths_for(slug):
    """Return (json, html, report) paths for a given paper slug, or legacy
    graphify-out/ if slug is None."""
    if slug:
        base = PAPERS_DIR / slug
        return (
            base / "paper_graph.json",
            base / "graphify-out" / "graph.html",
            base / "graphify-out" / "GRAPH_REPORT.md",
        )
    base = PROJECT_ROOT / "graphify-out"
    return base / "paper_graph.json", base / "graph.html", base / "GRAPH_REPORT.md"


def _active_slug():
    """Read papers/.current if present."""
    f = PAPERS_DIR / ".current"
    if f.exists():
        val = f.read_text(encoding="utf-8").strip()
        return val or None
    return None


DEFAULT_INPUT, DEFAULT_HTML, DEFAULT_REPORT = _paths_for(_active_slug())

# node type → color
TYPE_COLORS = {
    "CONCEPT": "#4CAF50",
    "CLAIM": "#2196F3",
    "EVIDENCE": "#FF9800",
    "ACTOR": "#9C27B0",
    "SCENARIO": "#F44336",
    "VARIABLE": "#795548",
}
DEFAULT_COLOR = "#90A4AE"

# edge relation → color
EDGE_COLORS = {
    "SUPPORTS": "rgba(76,175,80,0.4)",
    "CONTRADICTS": "rgba(244,67,54,0.5)",
    "CITES": "rgba(255,152,0,0.3)",
    "DEPENDS_ON": "rgba(33,150,243,0.4)",
    "OPERATIONALIZES": "rgba(121,85,72,0.3)",
    "PARTICIPATES_IN": "rgba(156,39,176,0.3)",
    "EXTENDS": "rgba(76,175,80,0.3)",
    "CONSTRAINS": "rgba(244,67,54,0.3)",
    "ANALOGOUS_TO": "rgba(158,158,158,0.3)",
}
DEFAULT_EDGE_COLOR = "rgba(255,255,255,0.12)"


def load_graph(path):
    """Load paper_graph.json and return nodes, edges, metadata."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("nodes", []), data.get("edges", []), data.get("metadata", {})


# ---------------------------------------------------------------------------
# Document scanner — deterministic extraction from raw markdown/text files
# ---------------------------------------------------------------------------

# Patterns for extraction
CITATION_RE = re.compile(r"\[@([\w\d_]+)\]")           # [@bloom2015working]
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")  # [[concept]]
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"^---\n(.*?\n)---", re.DOTALL)

# Simple keyword patterns to detect claim-like sentences
CLAIM_INDICATORS = [
    "表明", "说明", "证明", "显示", "意味着", "导致", "决定", "影响",
    "suggests", "indicates", "demonstrates", "shows", "implies",
    "argues", "concludes", "finds", "reveals", "determines",
]


def _slugify(text):
    """Convert text to a safe node ID."""
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "_", text.strip().lower())
    return slug.strip("_")[:60]


def _parse_frontmatter(text):
    """Extract tags and category from YAML frontmatter."""
    tags, category = [], ""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return tags, category
    fm = match.group(1)
    in_tags = False
    for line in fm.split("\n"):
        stripped = line.strip()
        if stripped.startswith("tags:"):
            # inline tags: tags: [a, b] or tags: a
            rest = stripped[5:].strip()
            if rest.startswith("["):
                tags.extend(t.strip().strip('"').strip("'")
                            for t in rest.strip("[]").split(",") if t.strip())
            elif rest:
                tags.append(rest)
            else:
                in_tags = True
            continue
        if in_tags:
            if stripped.startswith("- "):
                tags.append(stripped[2:].strip())
            else:
                in_tags = False
        if stripped.startswith("category:"):
            category = stripped.split(":", 1)[1].strip()
    return tags, category


def scan_documents(scan_dirs):
    """Scan directories for .md/.txt files, extract a knowledge graph.

    Extracts:
    - Documents as CONCEPT nodes (each file = a concept)
    - Section headings as sub-concepts
    - [@citation] references as EVIDENCE nodes
    - [[wikilinks]] as edges between documents
    - Sentences with claim indicators as CLAIM nodes
    - Frontmatter tags as grouping metadata
    """
    nodes = []
    edges = []
    seen_nodes = set()
    seen_citations = {}  # citation_key → node_id

    all_files = []
    for d in scan_dirs:
        dirpath = Path(d)
        if dirpath.is_file():
            all_files.append(dirpath)
        elif dirpath.is_dir():
            all_files.extend(sorted(dirpath.rglob("*.md")))
            all_files.extend(sorted(dirpath.rglob("*.txt")))

    if not all_files:
        return [], [], {}

    for fpath in all_files:
        try:
            text = fpath.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        rel_path = str(fpath)
        doc_name = fpath.stem
        doc_id = f"concept_{_slugify(doc_name)}"

        tags, category = _parse_frontmatter(text)

        # Document node
        if doc_id not in seen_nodes:
            nodes.append({
                "id": doc_id,
                "type": "CONCEPT",
                "label": doc_name,
                "section": category or str(fpath.parent.name),
                "source_file": rel_path,
                "tags": tags,
            })
            seen_nodes.add(doc_id)

        # Section headings → sub-concept nodes
        for match in HEADING_RE.finditer(text):
            level = len(match.group(1))
            title = match.group(2).strip()
            if level <= 2 and len(title) > 2:
                section_id = f"concept_{_slugify(doc_name)}_{_slugify(title)}"
                if section_id not in seen_nodes:
                    nodes.append({
                        "id": section_id,
                        "type": "CONCEPT",
                        "label": title,
                        "section": f"{doc_name}",
                        "source_file": rel_path,
                    })
                    seen_nodes.add(section_id)
                    edges.append({
                        "source": doc_id,
                        "target": section_id,
                        "relation": "EXTENDS",
                        "confidence": "EXTRACTED",
                        "confidence_score": 1.0,
                    })

        # Citations → EVIDENCE nodes + CITES edges
        for cite_key in CITATION_RE.findall(text):
            if cite_key not in seen_citations:
                cite_id = f"evidence_{_slugify(cite_key)}"
                nodes.append({
                    "id": cite_id,
                    "type": "EVIDENCE",
                    "label": cite_key,
                    "section": "",
                    "source_file": rel_path,
                })
                seen_citations[cite_key] = cite_id
                seen_nodes.add(cite_id)
            edges.append({
                "source": doc_id,
                "target": seen_citations[cite_key],
                "relation": "CITES",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
            })

        # Wikilinks → edges between documents
        for link_target in WIKILINK_RE.findall(text):
            target_id = f"concept_{_slugify(link_target)}"
            # Create target node if not seen (may be external reference)
            if target_id not in seen_nodes:
                nodes.append({
                    "id": target_id,
                    "type": "CONCEPT",
                    "label": link_target,
                    "section": "external",
                    "source_file": "",
                })
                seen_nodes.add(target_id)
            if doc_id != target_id:
                edges.append({
                    "source": doc_id,
                    "target": target_id,
                    "relation": "EXTENDS",
                    "confidence": "EXTRACTED",
                    "confidence_score": 1.0,
                })

        # Claim-like sentences (simple heuristic)
        sentences = re.split(r"[。.!！\n]", text)
        claim_count = 0
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 15 or len(sent) > 300:
                continue
            if any(ind in sent.lower() for ind in CLAIM_INDICATORS):
                claim_count += 1
                if claim_count > 5:  # cap per document
                    break
                claim_id = f"claim_{_slugify(doc_name)}_{claim_count}"
                short_label = sent[:80] + ("..." if len(sent) > 80 else "")
                if claim_id not in seen_nodes:
                    nodes.append({
                        "id": claim_id,
                        "type": "CLAIM",
                        "label": short_label,
                        "section": doc_name,
                        "source_file": rel_path,
                    })
                    seen_nodes.add(claim_id)
                    edges.append({
                        "source": doc_id,
                        "target": claim_id,
                        "relation": "SUPPORTS",
                        "confidence": "INFERRED",
                        "confidence_score": 0.7,
                    })
                    # Link claim to any citations in the same sentence
                    for cite_key in CITATION_RE.findall(sent):
                        if cite_key in seen_citations:
                            edges.append({
                                "source": seen_citations[cite_key],
                                "target": claim_id,
                                "relation": "SUPPORTS",
                                "confidence": "INFERRED",
                                "confidence_score": 0.7,
                            })

    # Deduplicate edges
    edge_keys = set()
    deduped_edges = []
    for e in edges:
        key = (e["source"], e["target"], e["relation"])
        if key not in edge_keys:
            edge_keys.add(key)
            deduped_edges.append(e)

    metadata = {
        "scan_dirs": [str(d) for d in scan_dirs],
        "total_files": len(all_files),
        "total_nodes": len(nodes),
        "total_edges": len(deduped_edges),
    }
    return nodes, deduped_edges, metadata


def compute_metrics(nodes, edges):
    """Compute degree, in-degree, out-degree for each node."""
    in_deg = defaultdict(int)
    out_deg = defaultdict(int)
    for e in edges:
        out_deg[e["source"]] += 1
        in_deg[e["target"]] += 1

    node_map = {}
    for n in nodes:
        nid = n["id"]
        ind = in_deg.get(nid, 0)
        outd = out_deg.get(nid, 0)
        degree = ind + outd
        ntype = n.get("type", n.get("file_type", ""))
        node_map[nid] = {
            **n,
            "in": ind,
            "out": outd,
            "degree": degree,
            "color": TYPE_COLORS.get(ntype, DEFAULT_COLOR),
            "size": max(8, min(40, 8 + degree * 2)),
        }
    return node_map


def find_orphan_evidence(node_map, edges):
    """Evidence nodes with no SUPPORTS or CITES edges."""
    evidence_ids = {nid for nid, n in node_map.items()
                    if n.get("type") == "EVIDENCE" or nid.startswith("evidence_")}
    connected = set()
    for e in edges:
        if e.get("relation") in ("SUPPORTS", "CITES"):
            connected.add(e["source"])
            connected.add(e["target"])
    return [node_map[nid] for nid in evidence_ids - connected if nid in node_map]


def find_unsupported_claims(node_map, edges):
    """Claim nodes with no SUPPORTS edge pointing to them."""
    claim_ids = {nid for nid, n in node_map.items()
                 if n.get("type") == "CLAIM" or nid.startswith("claim_")}
    supported = set()
    for e in edges:
        if e.get("relation") == "SUPPORTS":
            supported.add(e["target"])
    return [node_map[nid] for nid in claim_ids - supported if nid in node_map]


def find_uncontested_claims(node_map, edges):
    """Claim nodes with no CONTRADICTS edge."""
    claim_ids = {nid for nid, n in node_map.items()
                 if n.get("type") == "CLAIM" or nid.startswith("claim_")}
    contested = set()
    for e in edges:
        if e.get("relation") == "CONTRADICTS":
            contested.add(e["target"])
    return [node_map[nid] for nid in claim_ids - contested if nid in node_map]


def find_god_nodes(node_map, top_n=5):
    """Nodes with highest degree centrality."""
    return sorted(node_map.values(), key=lambda n: -n["degree"])[:top_n]


def find_communities(node_map, edges):
    """Simple community detection via connected components on undirected graph."""
    adj = defaultdict(set)
    for e in edges:
        s, t = e["source"], e["target"]
        if s in node_map and t in node_map:
            adj[s].add(t)
            adj[t].add(s)

    visited = set()
    communities = []
    for nid in node_map:
        if nid in visited:
            continue
        # BFS
        queue = [nid]
        component = []
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        communities.append(component)
    return communities


def find_cross_community_edges(edges, communities):
    """Edges that connect nodes in different communities."""
    node_to_community = {}
    for i, members in enumerate(communities):
        for nid in members:
            node_to_community[nid] = i
    bridges = []
    for e in edges:
        s_comm = node_to_community.get(e["source"])
        t_comm = node_to_community.get(e["target"])
        if s_comm is not None and t_comm is not None and s_comm != t_comm:
            bridges.append(e)
    return bridges


def generate_html(node_map, edges, out_path):
    """Generate self-contained interactive HTML with vis.js."""
    vis_nodes = []
    for nid, n in node_map.items():
        vis_nodes.append({
            "id": nid,
            "label": n.get("label", nid),
            "color": n["color"],
            "size": n["size"],
            "type": n.get("type", ""),
            "section": n.get("section", ""),
            "in": n["in"],
            "out": n["out"],
            "degree": n["degree"],
        })

    vis_edges = []
    for i, e in enumerate(edges):
        if e["source"] not in node_map or e["target"] not in node_map:
            continue
        rel = e.get("relation", "")
        vis_edges.append({
            "id": i,
            "from": e["source"],
            "to": e["target"],
            "relation": rel,
            "color": EDGE_COLORS.get(rel, DEFAULT_EDGE_COLOR),
            "dashes": rel == "CONTRADICTS",
        })

    nodes_json = json.dumps(vis_nodes, ensure_ascii=False)
    edges_json = json.dumps(vis_edges, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Paper Knowledge Graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; }}
#controls {{ position: fixed; top: 0; left: 0; right: 0; z-index: 10;
  background: rgba(26,26,46,0.95); padding: 10px 20px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
#controls input {{ padding: 6px 12px; border-radius: 6px; border: 1px solid #444;
  background: #16213e; color: #eee; width: 240px; font-size: 14px; }}
#controls select {{ padding: 6px 8px; border-radius: 6px; border: 1px solid #444;
  background: #16213e; color: #eee; font-size: 13px; }}
#controls .stat {{ font-size: 12px; color: #888; margin-left: auto; }}
.legend {{ display: flex; gap: 10px; }}
.legend span {{ display: flex; align-items: center; gap: 4px; font-size: 11px; color: #aaa; }}
.legend .dot {{ width: 10px; height: 10px; border-radius: 50%; }}
#graph {{ width: 100vw; height: 100vh; }}
#tooltip {{ position: fixed; display: none; background: rgba(22,33,62,0.96); border: 1px solid #555;
  border-radius: 8px; padding: 12px 16px; font-size: 13px; max-width: 320px; z-index: 20;
  pointer-events: none; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
#tooltip h3 {{ margin-bottom: 6px; font-size: 15px; }}
#tooltip .tag {{ display: inline-block; background: #333; border-radius: 4px;
  padding: 1px 6px; font-size: 11px; margin-right: 4px; }}
</style>
</head>
<body>
<div id="controls">
  <input id="search" type="text" placeholder="Search nodes...">
  <select id="typeFilter"><option value="">All types</option></select>
  <div class="legend">
    <span><span class="dot" style="background:#4CAF50"></span>Concept</span>
    <span><span class="dot" style="background:#2196F3"></span>Claim</span>
    <span><span class="dot" style="background:#FF9800"></span>Evidence</span>
    <span><span class="dot" style="background:#9C27B0"></span>Actor</span>
    <span><span class="dot" style="background:#F44336"></span>Scenario</span>
    <span><span class="dot" style="background:#795548"></span>Variable</span>
  </div>
  <span class="stat" id="stat"></span>
</div>
<div id="graph"></div>
<div id="tooltip"></div>
<script>
const rawNodes = {nodes_json};
const rawEdges = {edges_json};

const nodes = new vis.DataSet(rawNodes.map(n => ({{
  id: n.id, label: n.label,
  color: {{ background: n.color, border: n.color, highlight: {{ background: '#fff', border: n.color }} }},
  size: n.size, font: {{ color: '#ddd', size: Math.max(10, n.size * 0.6) }},
  nodeType: n.type, section: n.section, inCount: n.in, outCount: n.out, degree: n.degree
}})));
const edges = new vis.DataSet(rawEdges.map(e => ({{
  id: e.id, from: e.from, to: e.to, relation: e.relation,
  color: {{ color: e.color, highlight: '#ff0' }}, arrows: 'to',
  dashes: e.dashes || false
}})));

const container = document.getElementById('graph');
const network = new vis.Network(container, {{ nodes, edges }}, {{
  physics: {{ solver: 'forceAtlas2Based', forceAtlas2Based: {{ gravitationalConstant: -40, centralGravity: 0.005, springLength: 120 }},
    stabilization: {{ iterations: 200 }} }},
  interaction: {{ hover: true, tooltipDelay: 100 }},
}});

// populate type filter
const types = [...new Set(rawNodes.map(n => n.type).filter(Boolean))].sort();
const sel = document.getElementById('typeFilter');
types.forEach(t => {{ const o = document.createElement('option'); o.value = t; o.text = t; sel.add(o); }});
document.getElementById('stat').textContent = rawNodes.length + ' nodes · ' + rawEdges.length + ' edges';

// search
document.getElementById('search').addEventListener('input', e => {{
  const q = e.target.value.toLowerCase();
  if (!q) {{ nodes.forEach(n => nodes.update({{ id: n.id, hidden: false, opacity: 1 }})); return; }}
  nodes.forEach(n => {{
    const match = n.label.toLowerCase().includes(q) || n.id.toLowerCase().includes(q);
    nodes.update({{ id: n.id, hidden: false, opacity: match ? 1 : 0.1,
      font: {{ color: match ? '#fff' : '#333', size: match ? 14 : 8 }} }});
  }});
}});

// filter by type
sel.addEventListener('change', e => {{
  const t = e.target.value;
  nodes.forEach(n => {{
    const show = !t || n.nodeType === t;
    nodes.update({{ id: n.id, hidden: false, opacity: show ? 1 : 0.15,
      font: {{ color: show ? '#ddd' : '#444', size: show ? Math.max(10, n.size*0.6) : 8 }} }});
  }});
}});

// tooltip
const tip = document.getElementById('tooltip');
network.on('hoverNode', p => {{
  const n = nodes.get(p.node);
  tip.innerHTML = '<h3>' + n.label + '</h3>' +
    '<span class="tag">' + (n.nodeType || 'unknown') + '</span>' +
    (n.section ? '<span class="tag">§' + n.section + '</span>' : '') +
    '<br><br>In: ' + n.inCount + ' · Out: ' + n.outCount + ' · Degree: ' + n.degree;
  tip.style.display = 'block';
}});
network.on('blurNode', () => tip.style.display = 'none');
container.addEventListener('mousemove', e => {{
  tip.style.left = (e.clientX + 15) + 'px';
  tip.style.top = (e.clientY + 15) + 'px';
}});
</script>
</body>
</html>"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")


def generate_report(node_map, edges, communities, metadata, out_path):
    """Generate markdown analysis report."""
    nodes_list = list(node_map.values())
    if not nodes_list:
        out_path.write_text("# Graph Report\n\nEmpty graph — no nodes extracted.\n")
        return

    orphan_evidence = find_orphan_evidence(node_map, edges)
    unsupported_claims = find_unsupported_claims(node_map, edges)
    uncontested_claims = find_uncontested_claims(node_map, edges)
    god_nodes_list = find_god_nodes(node_map)
    cross_edges = find_cross_community_edges(edges, communities)

    # type distribution
    type_counts = defaultdict(int)
    for n in nodes_list:
        type_counts[n.get("type", "unknown")] += 1

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    max_degree = max(n["degree"] for n in nodes_list) if nodes_list else 0
    avg_degree = sum(n["degree"] for n in nodes_list) / len(nodes_list) if nodes_list else 0
    density = len(edges) / (len(nodes_list) * (len(nodes_list) - 1)) if len(nodes_list) > 1 else 0

    report = f"""# Paper Graph Report

> Auto-generated at {now}

## Summary

| Metric | Value |
|--------|-------|
| Total nodes | {len(nodes_list)} |
| Total edges | {len(edges)} |
| Communities | {len(communities)} |
| Network density | {density:.4f} |
| Average degree | {avg_degree:.1f} |
| Max degree | {max_degree} |

### Node Types

| Type | Count |
|------|-------|
"""
    for t in ["CONCEPT", "CLAIM", "EVIDENCE", "ACTOR", "SCENARIO", "VARIABLE"]:
        if type_counts.get(t, 0) > 0:
            report += f"| {t} | {type_counts[t]} |\n"

    report += f"""
## God Nodes (Top 5 by degree)

| Node | Type | Degree | In | Out |
|------|------|--------|-----|-----|
"""
    for n in god_nodes_list:
        report += f"| {n.get('label', n['id'])} | {n.get('type', '')} | {n['degree']} | {n['in']} | {n['out']} |\n"

    report += f"""
## Unsupported Claims ({len(unsupported_claims)})

Claims with no SUPPORTS edge — highest priority weakness.

"""
    if unsupported_claims:
        for n in unsupported_claims:
            section = f" (§{n['section']})" if n.get("section") else ""
            report += f"- **{n.get('label', n['id'])}**{section}\n"
    else:
        report += "None — all claims have supporting evidence.\n"

    report += f"""
## Uncontested Claims ({len(uncontested_claims)})

Claims with no CONTRADICTS edge — may indicate missing counterarguments.

"""
    if uncontested_claims:
        for n in uncontested_claims:
            section = f" (§{n['section']})" if n.get("section") else ""
            report += f"- {n.get('label', n['id'])}{section}\n"
    else:
        report += "None — all claims have counter-evidence.\n"

    report += f"""
## Orphan Evidence ({len(orphan_evidence)})

Evidence nodes not connected to any claim — unused citations.

"""
    if orphan_evidence:
        for n in orphan_evidence:
            report += f"- {n.get('label', n['id'])}\n"
    else:
        report += "None — all evidence is connected.\n"

    report += f"""
## Cross-Community Bridges ({len(cross_edges)})

Edges connecting different communities — the paper's structural backbone.

"""
    if cross_edges:
        for e in cross_edges[:10]:
            src = node_map.get(e["source"], {}).get("label", e["source"])
            tgt = node_map.get(e["target"], {}).get("label", e["target"])
            report += f"- {src} →[{e.get('relation', '')}]→ {tgt}\n"
    else:
        report += "None — single community or no cross-links.\n"

    report += f"""
## Communities ({len(communities)})

"""
    for i, members in enumerate(communities):
        member_labels = [node_map[m].get("label", m) for m in members if m in node_map]
        report += f"### Community {i} ({len(members)} nodes)\n\n"
        for label in sorted(member_labels)[:15]:
            report += f"- {label}\n"
        if len(member_labels) > 15:
            report += f"- ... and {len(member_labels) - 15} more\n"
        report += "\n"

    report += f"""## Diagnostic Summary

| Check | Status | Count |
|-------|--------|-------|
| Unsupported claims | {"PASS" if not unsupported_claims else "FAIL"} | {len(unsupported_claims)} |
| Uncontested claims | {"PASS" if not uncontested_claims else "WARN"} | {len(uncontested_claims)} |
| Orphan evidence | {"PASS" if not orphan_evidence else "WARN"} | {len(orphan_evidence)} |
| Disconnected clusters | {"PASS" if len(communities) <= 1 else "WARN"} | {len(communities)} |
| Cross-community bridges | {"OK" if len(cross_edges) >= 3 else "LOW"} | {len(cross_edges)} |
"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")


def merge_graphs(existing_json_path, new_nodes, new_edges):
    """Merge newly scanned nodes/edges into the existing graph file.

    Semantics: any node whose source_file appears in the new scan is replaced.
    All other existing nodes/edges are kept. Dedup by node id and edge triple.
    """
    try:
        data = json.loads(existing_json_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"nodes": [], "edges": [], "_meta": {}}

    old_nodes = data.get("nodes", [])
    old_edges = data.get("edges", [])
    rescanned_sources = {n.get("source_file") for n in new_nodes if n.get("source_file")}

    kept_nodes = [n for n in old_nodes if n.get("source_file") not in rescanned_sources]
    kept_ids = {n["id"] for n in kept_nodes}

    merged_nodes = list(kept_nodes)
    seen = set(kept_ids)
    for n in new_nodes:
        if n["id"] not in seen:
            merged_nodes.append(n)
            seen.add(n["id"])

    all_ids = {n["id"] for n in merged_nodes}
    kept_edges = [e for e in old_edges
                  if e["source"] in all_ids and e["target"] in all_ids
                  and e["source"] not in {x["id"] for x in new_nodes if x.get("source_file") in rescanned_sources}]
    edge_keys = {(e["source"], e["target"], e.get("relation", "")) for e in kept_edges}
    merged_edges = list(kept_edges)
    for e in new_edges:
        key = (e["source"], e["target"], e.get("relation", ""))
        if key in edge_keys:
            continue
        if e["source"] not in all_ids or e["target"] not in all_ids:
            continue
        merged_edges.append(e)
        edge_keys.add(key)

    data["nodes"] = merged_nodes
    data["edges"] = merged_edges
    data.setdefault("_meta", {})
    data["metadata"] = {
        "total_nodes": len(merged_nodes),
        "total_edges": len(merged_edges),
    }
    return data


def main():
    parser = argparse.ArgumentParser(description="Build paper knowledge graph visualization")
    parser.add_argument("--paper", default=None,
                        help="Paper slug (papers/<slug>/); overrides default paths. "
                             "If omitted, uses papers/.current or legacy graphify-out/.")
    parser.add_argument("--input", type=Path, default=None, help="Input JSON path override")
    parser.add_argument("--scan", nargs="*", default=None,
                        help="Scan directories for documents. Default: raw/ + papers/<slug>/paper.md")
    parser.add_argument("--html", type=Path, default=None, help="Output HTML path override")
    parser.add_argument("--report", type=Path, default=None, help="Output report path override")
    parser.add_argument("--html-only", action="store_true", help="Skip report generation")
    parser.add_argument("--save-json", action="store_true",
                        help="Save extracted graph to paper_graph.json (with --scan)")
    parser.add_argument("--merge", action="store_true",
                        help="With --save-json: merge into existing graph instead of overwriting")
    args = parser.parse_args()

    slug = args.paper or _active_slug()
    default_json, default_html, default_report = _paths_for(slug)
    input_path = args.input or default_json
    html_path = args.html or default_html
    report_path = args.report or default_report

    if args.scan is not None:
        scan_dirs = args.scan if args.scan else [
            str(PROJECT_ROOT / "raw"),
            str(PAPERS_DIR / slug / "paper.md") if slug else str(PROJECT_ROOT / "agents" / "paper.md"),
        ]
        print(f"Scanning: {', '.join(scan_dirs)}")
        nodes, edges, metadata = scan_documents(scan_dirs)
        if not nodes:
            print("No documents found or no content extracted")
            return
        print(f"Extracted: {len(nodes)} nodes, {len(edges)} edges from {metadata.get('total_files', '?')} files")
        if args.save_json:
            out_json = input_path
            out_json.parent.mkdir(parents=True, exist_ok=True)
            if args.merge and out_json.exists():
                merged = merge_graphs(out_json, nodes, edges)
                out_json.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
                nodes = merged["nodes"]
                edges = merged["edges"]
                metadata = merged.get("metadata", metadata)
                print(f"Merged into: {out_json} (now {len(nodes)} nodes, {len(edges)} edges)")
            else:
                # Preserve _meta block if present
                meta_block = {}
                if out_json.exists():
                    try:
                        meta_block = json.loads(out_json.read_text(encoding="utf-8")).get("_meta", {})
                    except Exception:
                        pass
                out_json.write_text(json.dumps(
                    {"_meta": meta_block, "nodes": nodes, "edges": edges, "metadata": metadata},
                    indent=2, ensure_ascii=False
                ), encoding="utf-8")
                print(f"Saved: {out_json}")
    else:
        if not input_path.exists():
            print(f"Error: {input_path} not found")
            print("Hint: use --scan to extract from documents, or scripts/autowrite kb-sync")
            return
        nodes, edges, metadata = load_graph(input_path)

    if not nodes:
        print("Empty graph — no nodes to visualize")
        return

    print(f"Loaded: {len(nodes)} nodes, {len(edges)} edges")

    node_map = compute_metrics(nodes, edges)
    communities = find_communities(node_map, edges)
    print(f"Communities: {len(communities)}")

    generate_html(node_map, edges, html_path)
    print(f"HTML: {html_path}")

    if not args.html_only:
        generate_report(node_map, edges, communities, metadata, report_path)
        print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
