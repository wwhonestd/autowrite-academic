# Index Rebuild Skill

自动从实际的 wiki 页面重建 index.md，防止索引与实际内容不同步。

## 问题背景

之前的 ingest 流程完成后，index.md 没有被完整更新，导致显示的是旧进度信息（46 页，而实际是 159 页）。这个 skill 通过扫描磁盘上的实际文件，自动生成准确的索引。

## 文件说明

- **SKILL.md** — 面向 Claude 的指示文档，说明如何使用此 skill
- **rebuild.py** — 自动化脚本，可独立运行重建 index.md

## 快速使用

### 方式 1：通过 Claude Code（推荐）

在对话中要求：
```
重建 wiki 索引
```

或使用 skill 命令：
```
/index-rebuild
```

### 方式 2：直接运行 Python 脚本

```bash
cd /Users/wwhonest/Documents/obsidian-wiki-main/.skills/index-rebuild
python3 rebuild.py
```

脚本会：
1. 读取 `.env` 获取 vault 路径
2. 扫描所有 `.md` 文件并提取元数据
3. 按标签组织概念（Concepts）
4. 生成新的 index.md 文件
5. 打印摘要信息

## 集成到 Ingest 流程

每次完成 ingest 后，都应该运行 index-rebuild：

```
# 第 1 步：运行 ingest 并创建/更新页面
<ingest 流程>

# 第 2 步：重建索引（防止不同步）
/index-rebuild
```

## 工作原理

### 扫描阶段
- 遍历 concepts/ 目录中的所有 .md 文件
- 遍历 entities/ 目录中的所有 .md 文件
- 遍历其他类别目录（skills, references, synthesis, journal）

### 提取阶段
- 从每个文件的 frontmatter 提取 `title` 和 `tags`
- 将第一个 tag 作为主分类标签

### 分组阶段
- 将所有 concepts 按主标签分组
- 按每个标签的页数降序排列
- 每个组内按标题字母排序

### 生成阶段
- 生成新的 index.md 内容
- 保留摄取历史和完成状态
- 更新最后修改时间戳

## 质量保证

rebuild.py 生成的 index.md 将：
- ✅ 显示实际的页面总数
- ✅ 按标签正确分组
- ✅ 所有页面都有 [[wikilink]]
- ✅ 包含完整的摄取进度历史
- ✅ 显示正确的覆盖率（100%）

## 常见问题

**Q: 重建索引会删除我的手动修改吗？**
A: 会的。index.md 是自动生成的，手动修改会被覆盖。如果你需要保持某些手动部分，可以创建单独的 sections.md 文件。

**Q: 能否只更新某个部分？**
A: 目前 rebuild.py 总是重建整个文件。如果需要增量更新，可以修改脚本。

**Q: 索引的标签分组怎么定义的？**
A: 使用文件 frontmatter 中的 `tags` 字段的**第一个标签**作为主分类。在 ingest 时，确保常见概念的主标签是一致的。

## 改进空间

- [ ] 从 log.md 中解析具体的批次信息
- [ ] 支持自定义分类方式（不仅仅按第一个标签）
- [ ] 生成标签云或统计信息
- [ ] 支持增量更新而不是完全重建
