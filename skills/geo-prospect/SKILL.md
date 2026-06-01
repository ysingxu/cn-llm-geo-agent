---
name: geo-prospect
description: >
  面向GEO机构的轻量级CRM，用于管理潜在客户和客户。通过完整销售漏斗跟踪线索：
  线索 → 已鉴定 → 已发提案 → 已成交 → 已失去。存储审计历史、备注、合同价值，
  并生成管道摘要。面向中国市场，定价以人民币计。
version: 1.0.0
tags: [geo, business, crm, prospect, pipeline, sales, china]
allowed-tools: Read, Write, Bash, Glob
---

# GEO潜在客户管理器（中国市场版）

## 命令

| 命令 | 功能 |
|---------|-------------|
| `/geo prospect new <域名>` | 创建新潜在客户（交互式提示） |
| `/geo prospect list` | 显示所有潜在客户及管道状态 |
| `/geo prospect list <状态>` | 筛选：线索、已鉴定、提案、成交、失去 |
| `/geo prospect show <id或域名>` | 查看完整潜在客户详情及历史 |
| `/geo prospect audit <id或域名>` | 运行快速GEO审计并保存到潜在客户记录 |
| `/geo prospect note <id或域名> "<文字>"` | 添加带时间戳的互动备注 |
| `/geo prospect status <id或域名> <新状态>` | 在管道中移动 |
| `/geo prospect won <id或域名> <月度价值>` | 标记为成交，设置合同价值（人民币） |
| `/geo prospect lost <id或域名> "<原因>"` | 标记为失去并注明原因 |
| `/geo prospect pipeline` | 可视化管道摘要及收入预测 |

---

## 数据结构

每个潜在客户存储为JSON记录：

```json
{
  "id": "PRO-001",
  "company": "示例科技有限公司",
  "domain": "example.com",
  "contact_email": "info@example.com",
  "contact_name": "张总",
  "industry": "企业软件",
  "country": "中国",
  "city": "上海",
  "status": "qualified",
  "geo_score": 32,
  "audit_date": "2026-06-01",
  "audit_file": "~/.geo-prospects/audits/example.com-2026-06-01.md",
  "proposal_file": "~/.geo-prospects/proposals/example.com-proposal.md",
  "monthly_value_cny": 0,
  "contract_start": null,
  "contract_months": 0,
  "notes": [
    {
      "date": "2026-06-01",
      "text": "初始GEO快速扫描。得分32/100 - 严重层级。强力GEO服务候选。"
    }
  ],
  "created_at": "2026-06-01",
  "updated_at": "2026-06-01"
}
```

---

## 管道显示示例

```
GEO潜在客户管道 — 2026年6月
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID       域名                    公司              状态        得分   月值
───────  ──────────────────────  ────────────────  ──────────  ─────  ──────
PRO-001  example.com             示例科技          已鉴定      32/100  ¥27K
PRO-002  acme.cn                 艾可米科技        线索        —       —
PRO-003  bigshop.com.cn          大商城            成交        41/100  ¥36K

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
管道：1条线索 | 1个已鉴定 | 0个提案 | 1个成交 | 0个失去
已承诺月收入：¥36,000 | 管道价值：¥27,000
```

---

## 管道阶段定义

| 状态 | 含义 | 典型后续行动 |
|--------|---------|---------------------|
| `lead` | 已发现，尚未联系 | 运行快速审计，评估机会 |
| `qualified` | 审计完成，确认痛点 | 生成提案 |
| `proposal` | 提案已发，等待决定 | 跟进，回答问题 |
| `won` | 合同已签，活跃客户 | 运行完整审计，开始启动 |
| `lost` | 交易关闭失败 | 记录原因供将来参考 |

---

## 存储位置

所有数据存储在 `~/.geo-prospects/`：
```
~/.geo-prospects/
├── prospects.json          # 主CRM数据库
├── audits/                 # 快速审计快照
│   └── example.com-2026-06-01.md
└── proposals/              # 生成的提案
    └── example.com-proposal.md
```

创建目录（若不存在）：`mkdir -p ~/.geo-prospects/audits ~/.geo-prospects/proposals`
