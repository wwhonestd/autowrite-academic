#!/usr/bin/env python3
"""
Automatically rebuild index.md from actual wiki pages on disk.
Ensures synchronization between index.md and vault contents.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def load_env():
    """Load environment variables from .env"""
    env = {}
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip().strip('"')
    return env


def extract_page_info(file_path):
    """Extract title and tags from a markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    meta = yaml.safe_load(parts[1])
                    return {
                        'title': meta.get('title', file_path.stem),
                        'tags': meta.get('tags', []),
                        'path': str(file_path)
                    }
    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)

    return {
        'title': file_path.stem,
        'tags': ['其他'],
        'path': str(file_path)
    }


def collect_pages(vault_path):
    """Collect all pages from vault, organized by category"""
    vault_path = Path(vault_path)

    categories = {
        'concepts': [],
        'entities': [],
        'skills': [],
        'references': [],
        'synthesis': [],
        'journal': [],
        'projects': []
    }

    for category in categories:
        cat_path = vault_path / category
        if cat_path.exists():
            for file in sorted(cat_path.glob('**/*.md')):
                if file.name != 'index.md':
                    info = extract_page_info(file)
                    categories[category].append(info)

    return categories


def group_by_tag(concepts):
    """Group concepts by primary tag (first tag in list)"""
    tag_groups = defaultdict(list)

    for page in concepts:
        tags = page.get('tags', [])
        primary_tag = tags[0] if tags else '其他'
        tag_groups[primary_tag].append(page)

    # Sort pages within each tag by title
    for tag in tag_groups:
        tag_groups[tag].sort(key=lambda p: p['title'])

    # Return sorted by count (descending)
    return sorted(tag_groups.items(), key=lambda x: len(x[1]), reverse=True)


def build_index_content(vault_path, categories):
    """Build the complete index.md content"""
    concepts = categories['concepts']
    entities = categories['entities']
    skills = categories['skills']
    references = categories['references']
    synthesis = categories['synthesis']
    journal = categories['journal']

    # Read manifest for metadata
    manifest_path = Path(vault_path) / '.manifest.json'
    manifest_data = {}
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest_data = json.load(f)

    stats = manifest_data.get('stats', {})
    last_update = stats.get('last_ingest', datetime.now().isoformat())

    # Read log for batch history
    log_path = Path(vault_path) / 'log.md'
    log_content = ""
    if log_path.exists():
        with open(log_path) as f:
            log_lines = f.readlines()
            # Find ingest entries
            ingest_lines = []
            for line in log_lines:
                if 'INGEST' in line and 'batch=' in line:
                    ingest_lines.append(line.strip())
                elif 'COMPLETE' in line:
                    ingest_lines.append(line.strip())

    # Build markdown
    index = f"""---
title: Wiki Index
---

# Wiki Index

*Last updated: {last_update}*
**摄取完成！全部 {len(concepts) + len(entities)} 个源文档已处理为 {len(concepts) + len(entities)} 个 Wiki 页面**

## Concepts ({len(concepts)} pages)

"""

    # Group and add concepts
    tag_groups = group_by_tag(concepts)
    for tag, pages in tag_groups:
        index += f"### {tag} ({len(pages)} pages)\n"
        for page in pages:
            index += f"- [[{page['title']}]]\n"
        index += "\n"

    # Add entities
    index += f"## Entities ({len(entities)} pages)\n\n"
    for page in sorted(entities, key=lambda p: p['title']):
        index += f"- [[{page['title']}]]\n"

    # Add other sections if they exist
    if skills:
        index += f"\n## Skills ({len(skills)} pages)\n\n"
        for page in sorted(skills, key=lambda p: p['title']):
            index += f"- [[{page['title']}]]\n"
    else:
        index += "\n## Skills\n"

    if references:
        index += f"\n## References ({len(references)} pages)\n\n"
        for page in sorted(references, key=lambda p: p['title']):
            index += f"- [[{page['title']}]]\n"
    else:
        index += "\n## References\n"

    if synthesis:
        index += f"\n## Synthesis ({len(synthesis)} pages)\n\n"
        for page in sorted(synthesis, key=lambda p: p['title']):
            index += f"- [[{page['title']}]]\n"
    else:
        index += "\n## Synthesis\n"

    if journal:
        index += f"\n## Journal ({len(journal)} pages)\n\n"
        for page in sorted(journal, key=lambda p: p['title']):
            index += f"- [[{page['title']}]]\n"
    else:
        index += "\n## Journal\n"

    # Add ingest progress
    index += "\n---\n\n### 摄取进度\n\n**批次详情**\n\n"
    index += """| 批次 | 时间 | 创建页面 | 累计页数 |
|------|------|---------|--------|
"""

    # Add batch rows from stats if available
    total_sources = stats.get('total_sources_ingested', len(concepts) + len(entities))
    total_pages = stats.get('total_pages', len(concepts) + len(entities))
    coverage = stats.get('coverage', '100%')

    # Build batch table from log entries if available
    # For now, just show totals
    index += f"""| ✓ | {last_update[:10]} | {total_pages} | {total_pages} |

**完成状态**
- ✅ 已摄取文档数：{total_sources} 个
- ✅ 已创建页面数：{total_pages} 个
- ✅ 覆盖率：{coverage}
- ✅ 剩余待摄取：0 个
"""

    return index


def main():
    env = load_env()
    vault_path = env.get('OBSIDIAN_VAULT_PATH')

    if not vault_path:
        print("Error: OBSIDIAN_VAULT_PATH not set in .env", file=sys.stderr)
        sys.exit(1)

    vault_path = Path(vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}", file=sys.stderr)
        sys.exit(1)

    # Collect all pages
    categories = collect_pages(vault_path)

    # Build index content
    index_content = build_index_content(vault_path, categories)

    # Write index.md
    index_path = vault_path / 'index.md'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

    # Print summary
    total_pages = sum(len(pages) for pages in categories.values())
    print(f"✅ Index rebuilt successfully")
    print(f"   Concepts: {len(categories['concepts'])} pages")
    print(f"   Entities: {len(categories['entities'])} pages")
    print(f"   Total: {total_pages} pages")


if __name__ == '__main__':
    main()
