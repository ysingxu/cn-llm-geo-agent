# 中国LLM GEO-SEO — Claude Code Skill

> 面向中国AI搜索平台的生成式引擎优化工具  
> 专为豆包、元宝、DeepSeek、文心一言、通义千问优化

---

## 什么是GEO？

**生成式引擎优化（GEO）** 是优化网络内容使其被AI系统发现、理解、引用和推荐的实践。这与传统SEO（针对搜索引擎排名）不同——GEO针对的是**AI引用和推荐**。

对于中国市场，这意味着针对以下平台优化：
- **豆包**（字节跳动）— 月活用户1亿+
- **元宝**（腾讯混元）— 深度整合微信生态
- **DeepSeek** — 技术/研究领域高引用率
- **文心一言**（百度）— 国内最大搜索引擎
- **通义千问**（阿里云）— 电商和企业场景

---

## 快速安装

### Windows（Git Bash）
```bash
git clone https://github.com/lejiazhang/cn-llm-geo-agent.git
cd cn-llm-geo-agent
bash install-win.sh
```

### macOS / Linux
```bash
git clone https://github.com/lejiazhang/cn-llm-geo-agent.git
cd cn-llm-geo-agent
bash install.sh
```

### 一行安装（macOS / Linux）
```bash
git clone https://github.com/lejiazhang/cn-llm-geo-agent.git && cd cn-llm-geo-agent && bash install.sh
```

### 手动安装
将以下目录复制到 `~/.claude/`：
```
geo/        → ~/.claude/skills/geo/
skills/*    → ~/.claude/skills/geo-*/
agents/*    → ~/.claude/agents/
```

---

## 快速入门

安装后，在 Claude Code 中使用以下命令：

```bash
# 完整GEO审计（分析所有5个中国平台）
/geo audit https://example.com

# 60秒可见性快照
/geo quick https://example.com

# 检查中国AI爬虫访问权限
/geo crawlers https://example.com

# 平台专项分析（豆包/文心/DeepSeek等）
/geo platforms https://example.com

# 品牌提及扫描（知乎/B站/百度百科/微博）
/geo brands https://example.com

# 评估内容AI可引用性
/geo citability https://example.com/article

# 生成或分析llms.txt（含中文内容）
/geo llmstxt https://example.com

# 技术SEO审计（含ICP备案、百度站长检查）
/geo technical https://example.com

# 内容质量和E-E-A-T评估
/geo content https://example.com

# 生成客户可交付报告
/geo report https://example.com
```

---

## 所有命令

| 命令 | 说明 |
|---------|-------------|
| `/geo audit <url>` | 完整GEO + SEO审计（5个并行子代理） |
| `/geo quick <url>` | 60秒可见性快照 |
| `/geo page <url>` | 深度单页GEO分析 |
| `/geo citability <url>` | AI可引用性得分（0-100） |
| `/geo crawlers <url>` | AI爬虫访问检查（含中国平台） |
| `/geo llmstxt <url>` | 分析或生成llms.txt（中文版） |
| `/geo brands <url>` | 品牌提及扫描（知乎/B站/百度百科/微博） |
| `/geo platforms <url>` | 豆包/元宝/DeepSeek/文心一言/通义千问专项优化 |
| `/geo schema <url>` | 结构化数据检测、验证和生成 |
| `/geo technical <url>` | 技术SEO审计（含ICP备案） |
| `/geo content <url>` | 内容质量与E-E-A-T评估 |
| `/geo report <url>` | 生成客户可交付GEO报告 |
| `/geo report-pdf <url>` | 生成含图表的专业PDF报告 |
| `/geo prospect <cmd>` | 潜在客户CRM管理 |
| `/geo proposal <domain>` | 根据审计数据自动生成客户提案 |
| `/geo compare <domain>` | 月度对比报告 |
| `/geo update` | 从上游拉取最新更新 |

---

## 评分方法

综合GEO得分（0-100）是六个类别得分的加权平均：

| 类别 | 权重 | 衡量内容 |
|------|------|---------|
| AI可引用性 | 25% | 内容对AI系统的可提取程度 |
| 品牌权威 | 20% | 知乎/B站/百度百科/微博的第三方提及 |
| 内容E-E-A-T | 20% | 经验、专业知识、权威性、可信度 |
| 技术基础 | 15% | AI爬虫访问、SSR、速度、ICP备案 |
| 结构化数据 | 10% | Schema.org标记质量和完整性 |
| 平台优化 | 10% | 豆包/元宝/DeepSeek/文心一言/通义千问就绪度 |

---

## 中国市场特定功能

与全球版本相比，本工具新增以下中国市场特定功能：

### 平台覆盖
- **豆包**（字节跳动/今日头条生态）
- **元宝**（腾讯混元/微信/知乎生态）
- **DeepSeek**（技术/学术优先）
- **文心一言**（百度/百度百科/百家号生态）
- **通义千问**（阿里巴巴/优酷/淘宝生态）

### 爬虫检查
- Baiduspider（文心一言/百度）
- Bytespider（豆包/字节跳动）
- Sogouwebspider（元宝/腾讯）
- DeepSeekBot（DeepSeek）

### 品牌平台扫描
- 知乎（权重30%）
- B站/Bilibili（权重25%）
- 百度百科（权重20%）
- 微博（权重15%）
- 小红书/微信/抖音（补充，权重10%）

### 合规检查
- ICP备案验证
- 《个人信息保护法》隐私政策合规
- 企业认证（微信蓝V、百度蓝V等）
- 防火长城屏蔽资源检测

### llms.txt增强
- 简体中文内容描述
- 中国平台账号信息板块
- 中国用户相关关键事实

---

## 先决条件

- **Claude Code CLI** — `npm install -g @anthropic-ai/claude-code`
- **Python 3.8+** — 用于网页获取脚本
- **Git** — 用于更新
- **pandoc + Chrome**（可选）— 用于PDF报告生成

---

## 目录结构

```
geo/                    ← 主技能（/geo 命令入口）
skills/
  geo-audit/           ← 完整审计编排
  geo-citability/      ← AI可引用性评分
  geo-crawlers/        ← 爬虫访问分析（含中国平台）
  geo-llmstxt/         ← llms.txt分析与生成（中文版）
  geo-brand-mentions/  ← 品牌提及扫描（知乎/B站/微博等）
  geo-platform-optimizer/ ← 豆包/元宝/DeepSeek/文心/千问优化
  geo-schema/          ← 结构化数据审计与生成
  geo-technical/       ← 技术SEO（含ICP备案检查）
  geo-content/         ← 内容质量与E-E-A-T（中国市场版）
  geo-report/          ← 客户报告生成
  geo-report-pdf/      ← PDF报告生成
  geo-prospect/        ← 潜在客户CRM
  geo-proposal/        ← 客户提案（人民币定价）
  geo-compare/         ← 月度对比报告
  geo-update/          ← 技能更新管理
agents/
  geo-ai-visibility.md    ← AI可见性分析代理
  geo-platform-analysis.md ← 平台分析代理（中国5平台）
  geo-technical.md        ← 技术SEO代理
  geo-content.md          ← 内容质量代理
  geo-schema.md           ← 结构化数据代理
scripts/
  fetch_page.py        ← 网页抓取工具
templates/             ← PDF报告模板
```

---

## 许可证

MIT License — 可自由使用、修改和分发。
