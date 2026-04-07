---
name: index-rebuild
description: >
  Automatically rebuild the wiki index.md from the actual wiki pages on disk.
  Run this after every ingest to ensure index.md stays synchronized with vault contents.
  Use when you notice index.md is outdated or mismatched with actual pages.
---

# Index Rebuild — Synchronize index.md with Wiki Contents

This skill ensures `index.md` always reflects the **actual state** of the wiki by reading all pages on disk and regenerating the index.

## When to Use

- **After every ingest** — Call this as the final step to prevent desynchronization
- **When you notice index.md is stale** — If the page count or listing doesn't match reality
- **After wiki-rebuild** — When pages have been reorganized
- **On request** — User asks "rebuild index" or "fix the index"

## How It Works

### Step 1: Scan the Vault

Read all pages from disk:
```bash
find VAULT_PATH/concepts -name "*.md" | wc -l
find VAULT_PATH/entities -name "*.md" | wc -l
find VAULT_PATH/skills -name "*.md" | wc -l
find VAULT_PATH/references -name "*.md" | wc -l
find VAULT_PATH/synthesis -name "*.md" | wc -l
find VAULT_PATH/journal -name "*.md" | wc -l
find VAULT_PATH/projects -name "*.md" | wc -l
```

### Step 2: Extract Metadata

For each `.md` file found, extract:
- **title** from frontmatter
- **category** from directory path
- **tags** from frontmatter
- Order by title alphabetically

### Step 3: Group by Tag

Group concepts by their **primary tag** (first tag in the tags list). This creates natural sections.

### Step 4: Generate Index Structure

Create a new index.md with:
- **Header section** — summarizing total counts (X concepts, Y entities, etc.)
- **Concepts section** — grouped by tag, with page counts and wikilinks
- **Entities section** — alphabetically sorted
- **Other sections** — Skills, References, Synthesis, Journal (if pages exist)
- **Manifest info** — Last updated timestamp from `.manifest.json`
- **Ingest history** — Log of all batches from `log.md`
- **Final status** — Coverage percentage and completion metrics

### Step 5: Write New index.md

Replace the existing `index.md` with the newly generated version.

## Template Structure

```markdown
---
title: Wiki Index
---

# Wiki Index

*Last updated: [TIMESTAMP]*
**摄取完成！全部 N 个源文档已处理为 N 个 Wiki 页面**

## Concepts (N pages)

### [TAG] (N pages)
- [[Page 1]]
- [[Page 2]]

## Entities (N pages)

- [[Entity 1]]
- [[Entity 2]]

## Skills
...
## References
...
## Synthesis
...
## Journal
...

---

### 摄取进度
[Batch table from log.md]

**完成状态**
- ✅ 已摄取文档数：N 个
- ✅ 已创建页面数：N 个
- ✅ 覆盖率：100%
- ✅ 剩余待摄取：0 个
```

## Integration Point

**Add this to the end of wiki-ingest Step 7:**

```
### Step 8: Rebuild Index (CRITICAL)

After all pages are written and manifest is updated, **always run index-rebuild** to ensure index.md is synchronized:

1. Use the `index-rebuild` skill to regenerate index.md
2. Verify the page counts match the manifest
3. Spot-check a few wikilinks work correctly
```

## Quality Checklist

- [ ] All concept pages are discoverable in index.md (count matches `find concepts -name "*.md"`)
- [ ] All entity pages are listed (count matches `find entities -name "*.md"`)
- [ ] Page counts by tag are accurate
- [ ] Manifest timestamp is current
- [ ] Batch history table is complete
- [ ] Header shows actual totals, not outdated summary
