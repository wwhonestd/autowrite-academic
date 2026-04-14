# Paper Graph Report

> Auto-generated at 2026-04-14 08:19

## Summary

| Metric | Value |
|--------|-------|
| Total nodes | 44 |
| Total edges | 45 |
| Communities | 1 |
| Network density | 0.0238 |
| Average degree | 2.0 |
| Max degree | 43 |

### Node Types

| Type | Count |
|------|-------|
| CONCEPT | 11 |
| CLAIM | 5 |
| EVIDENCE | 28 |

## God Nodes (Top 5 by degree)

| Node | Type | Degree | In | Out |
|------|------|--------|-----|-----|
| paper | CONCEPT | 43 | 0 | 43 |
| latin_decentralization_trap | EVIDENCE | 2 | 1 | 1 |
| laac_inequality_politics | EVIDENCE | 2 | 1 | 1 |
| - 地方权力分割导致的政策不连贯 [@latin_decentralization_trap] | CLAIM | 2 | 2 | 0 |
| - 社会不平等加剧导致的政治极化 [@laac_inequality_politics] | CLAIM | 2 | 2 | 0 |

## Unsupported Claims (0)

Claims with no SUPPORTS edge — highest priority weakness.

None — all claims have supporting evidence.

## Uncontested Claims (5)

Claims with no CONTRADICTS edge — may indicate missing counterarguments.

- thesis: "正确政绩观通过在发展与安全的权衡中确立党的领导地位、构建长期制度激励、强化预防性风险治理，使中国在跨越中等收入阶段时成功规避了拉美式的'经济脆... (§paper)
- - 社会不平等加剧导致的政治极化 [@laac_inequality_politics] (§paper)
- 本文通过十年同周期对标研究，系统分析了正确政绩观如何通过改变地方政府的评价标准，从源头防止片面追求增长导致的结构失衡、社会矛盾和治理衰退，形成了中国式现代化规避... (§paper)
- - 合成对照法证明：三分之二的衰落源于政策制度变化（非外部冲击） (§paper)
- - 地方权力分割导致的政策不连贯 [@latin_decentralization_trap] (§paper)

## Orphan Evidence (0)

Evidence nodes not connected to any claim — unused citations.

None — all evidence is connected.

## Cross-Community Bridges (0)

Edges connecting different communities — the paper's structural backbone.

None — single community or no cross-links.

## Communities (1)

### Community 0 (44 nodes)

- - 合成对照法证明：三分之二的衰落源于政策制度变化（非外部冲击）
- - 地方权力分割导致的政策不连贯 [@latin_decentralization_trap]
- - 社会不平等加剧导致的政治极化 [@laac_inequality_politics]
- 1. Introduction
- 2. Literature Review
- 3. Theoretical Framework：发展-安全统筹的三维模型
- 4. Methodology
- 5. Findings
- 6. Discussion
- 7. Conclusion
- Abstract
- References
- argentina_trap
- brazil_stagnation
- brazil_stagnation_politics
- ... and 29 more

## Diagnostic Summary

| Check | Status | Count |
|-------|--------|-------|
| Unsupported claims | PASS | 0 |
| Uncontested claims | WARN | 5 |
| Orphan evidence | PASS | 0 |
| Disconnected clusters | PASS | 1 |
| Cross-community bridges | LOW | 0 |
