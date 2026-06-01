---
name: geo
description: >
  面向中国大语言模型平台的GEO分析工具。针对豆包、元宝（腾讯混元）、DeepSeek、
  文心一言（百度）、通义千问（阿里云）等国内AI搜索引擎优化网站内容，同时保持
  传统SEO基础。执行完整GEO审计、可引用性评分、AI爬虫分析、llms.txt生成、
  品牌提及扫描、平台专项优化、结构化数据标记、技术SEO、内容质量（E-E-A-T）
  以及客户GEO报告生成。当用户说"geo"、"seo"、"审计"、"AI搜索"、"AI可见性"、
  "优化"、"可引用性"、"llms.txt"、"结构化数据"、"品牌提及"、"GEO报告"，
  或提供任何URL进行分析时触发。
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write
---

# 中国LLM平台 GEO-SEO 分析工具 — Claude Code Skill（2026年）

> **核心理念：** GEO优先，SEO支撑。中国AI搜索正在快速取代传统搜索。
> 本工具专为中国市场优化，面向豆包、元宝、DeepSeek、文心一言、通义千问等主流平台。

---

## 快速参考

| 命令 | 功能说明 |
|---------|-------------|
| `/geo audit <url>` | 完整GEO + SEO审计（并行子代理） |
| `/geo page <url>` | 深度单页GEO分析 |
| `/geo citability <url>` | 评估内容AI可引用性得分 |
| `/geo crawlers <url>` | 检查AI爬虫访问权限（robots.txt分析） |
| `/geo llmstxt <url>` | 分析或生成llms.txt文件 |
| `/geo brands <url>` | 扫描品牌在AI引用平台的提及情况 |
| `/geo platforms <url>` | 平台专项优化（豆包、元宝、DeepSeek等） |
| `/geo schema <url>` | 检测、验证并生成结构化数据 |
| `/geo technical <url>` | 传统技术SEO审计 |
| `/geo content <url>` | 内容质量与E-E-A-T评估 |
| `/geo report <url>` | 生成客户可交付GEO报告 |
| `/geo report-pdf <url>` | 生成含图表和评分的专业PDF报告 |
| `/geo quick <url>` | 60秒GEO可见性快照 |
| `/geo prospect <cmd>` | CRM轻量版：管理潜在客户销售漏斗 |
| `/geo proposal <domain>` | 根据审计数据自动生成客户提案 |
| `/geo compare <domain>` | 月度对比报告：向客户展示分数提升 |
| `/geo update` | 从上游拉取最新GEO技能更新 |

---

## 市场背景（为何GEO在中国重要）

| 指标 | 数值 | 来源 |
|--------|-------|--------|
| 豆包月活用户（2025） | 1亿+ | 字节跳动 |
| 通义千问月活用户（2025） | 5000万+ | 阿里云 |
| 文心一言月活用户（2025） | 3亿+ | 百度 |
| DeepSeek全球用户（2025） | 8000万+ | DeepSeek官方 |
| 元宝（腾讯混元）月活 | 5000万+ | 腾讯 |
| 中国AI搜索渗透率增速 | +340% YoY（2024-2025） | 行业数据 |
| AI流量转化率 vs 传统有机流量 | 高3-5倍 | 行业调研 |
| 百度AI搜索每月处理量 | 50亿+次查询 | 百度 |
| 投入GEO优化的中国企业比例 | 仅18% | 行业调研（2025） |

---

## 编排逻辑

### 完整审计（`/geo audit <url>`）

**第一阶段：发现（顺序执行）**
1. 获取首页HTML（curl或WebFetch）
2. 检测业务类型（SaaS、本地服务、电商、内容发布、机构、其他）
3. 从sitemap.xml或内部链接提取关键页面（最多50页）

**第二阶段：并行分析（委派给子代理）**
同时启动以下5个子代理：

| 子代理 | 文件 | 职责 |
|----------|------|---------------|
| geo-ai-visibility | `agents/geo-ai-visibility.md` | GEO审计、可引用性、AI爬虫、llms.txt、品牌提及 |
| geo-platform-analysis | `agents/geo-platform-analysis.md` | 平台专项优化（豆包、元宝、DeepSeek、文心一言、通义千问） |
| geo-technical | `agents/geo-technical.md` | 技术SEO、核心指标、可抓取性、可索引性 |
| geo-content | `agents/geo-content.md` | 内容质量、E-E-A-T、可读性、AI内容检测 |
| geo-schema | `agents/geo-schema.md` | 结构化数据检测、验证、生成 |

**第三阶段：综合（顺序执行）**
1. 汇总所有子代理报告
2. 计算综合GEO得分（0-100）
3. 生成优先行动计划
4. 输出客户可用报告

### 评分方法

| 类别 | 权重 | 衡量标准 |
|----------|--------|-------------|
| AI可引用性与可见性 | 25% | 段落评分、答案块质量、AI爬虫访问 |
| 品牌权威信号 | 20% | 知乎、B站、百度百科、微博提及；实体存在 |
| 内容质量与E-E-A-T | 20% | 专业信号、原创数据、作者资质 |
| 技术基础 | 15% | SSR、核心Web指标、可抓取性、移动端、安全 |
| 结构化数据 | 10% | Schema完整性、JSON-LD验证、富结果资格 |
| 平台优化 | 10% | 平台专项就绪度（豆包、DeepSeek、文心一言等） |

---

## 业务类型检测

分析首页，识别以下信号：

| 类型 | 信号 |
|------|---------|
| **SaaS/软件** | 定价页面、"免费试用"、"注册"、/app、/dashboard、API文档 |
| **本地服务** | 电话号码、地址、"附近"、地图嵌入、服务区域 |
| **电商** | 商品页面、购物车、"加入购物车"、价格元素、商品结构数据 |
| **内容发布** | 博客、文章、作者署名、发布日期、文章结构数据 |
| **机构/服务** | 案例研究、作品集、"我们的服务"、客户logo、推荐语 |
| **其他** | 默认 — 应用通用GEO最佳实践 |

根据检测到的类型调整建议。本地商家需要LocalBusiness schema和百度地图优化。SaaS需要SoftwareApplication schema和对比页面策略。电商需要Product schema和评价聚合。

---

## 子技能（14个专业组件）

| # | 技能 | 目录 | 用途 |
|---|-------|-----------|---------|
| 1 | geo-audit | `skills/geo-audit/` | 完整审计编排与评分 |
| 2 | geo-citability | `skills/geo-citability/` | 段落级AI引用就绪度 |
| 3 | geo-crawlers | `skills/geo-crawlers/` | AI爬虫访问与robots.txt |
| 4 | geo-llmstxt | `skills/geo-llmstxt/` | llms.txt标准分析与生成 |
| 5 | geo-brand-mentions | `skills/geo-brand-mentions/` | 品牌在AI引用平台的存在度 |
| 6 | geo-platform-optimizer | `skills/geo-platform-optimizer/` | 平台专项AI搜索优化 |
| 7 | geo-schema | `skills/geo-schema/` | 面向AI可发现性的结构化数据 |
| 8 | geo-technical | `skills/geo-technical/` | 技术SEO基础 |
| 9 | geo-content | `skills/geo-content/` | 内容质量与E-E-A-T |
| 10 | geo-report | `skills/geo-report/` | 客户可交付报告生成 |
| 11 | geo-prospect | `skills/geo-prospect/` | CRM轻量版潜在客户与客户管道管理 |
| 12 | geo-proposal | `skills/geo-proposal/` | 根据审计数据自动生成客户提案 |
| 13 | geo-compare | `skills/geo-compare/` | 月度对比跟踪与进度报告 |
| 14 | geo-update | `skills/geo-update/` | 从上游仓库拉取最新更新 |

---

## 子代理（5个并行工作者）

| 代理 | 文件 | 使用的技能 |
|-------|------|-------------|
| geo-ai-visibility | `agents/geo-ai-visibility.md` | geo-citability, geo-crawlers, geo-llmstxt, geo-brand-mentions |
| geo-platform-analysis | `agents/geo-platform-analysis.md` | geo-platform-optimizer |
| geo-technical | `agents/geo-technical.md` | geo-technical |
| geo-content | `agents/geo-content.md` | geo-content |
| geo-schema | `agents/geo-schema.md` | geo-schema |

---

## 输出文件

所有命令生成结构化输出：

| 命令 | 输出文件 |
|---------|------------|
| `/geo audit` | `GEO-AUDIT-REPORT.md` |
| `/geo page` | `GEO-PAGE-ANALYSIS.md` |
| `/geo citability` | `GEO-CITABILITY-SCORE.md` |
| `/geo crawlers` | `GEO-CRAWLER-ACCESS.md` |
| `/geo llmstxt` | `llms.txt`（可直接部署） |
| `/geo brands` | `GEO-BRAND-MENTIONS.md` |
| `/geo platforms` | `GEO-PLATFORM-OPTIMIZATION.md` |
| `/geo schema` | `GEO-SCHEMA-REPORT.md` + 生成的JSON-LD |
| `/geo technical` | `GEO-TECHNICAL-AUDIT.md` |
| `/geo content` | `GEO-CONTENT-ANALYSIS.md` |
| `/geo report` | `GEO-CLIENT-REPORT.md`（演示就绪） |
| `/geo report-pdf` | `GEO-REPORT.pdf`（含图表的专业PDF） |
| `/geo quick` | 内联摘要（无文件） |
| `/geo prospect` | 更新 `~/.geo-prospects/prospects.json` |
| `/geo proposal` | `~/.geo-prospects/proposals/<domain>-proposal-<date>.md` |
| `/geo compare` | `~/.geo-prospects/reports/<domain>-monthly-<YYYY-MM>.md` |

---

## PDF报告生成

`/geo report-pdf <url>` 命令将 `GEO-AUDIT-REPORT.md` 转换为样式精美、客户可用的PDF。

### 环境要求
- **pandoc** — `winget install pandoc` 或 `brew install pandoc`
- **Google Chrome** — 标准安装即可

### PDF内容
- **封面页** — 深蓝渐变、GEO得分徽章、品牌/域名/日期/位置元数据
- **色码得分表** — 含 `XX/100` 的单元格自动着色：绿/蓝/琥珀/橙/红
- **严重性标签发现** — 严重/高/中/低区块带彩色左边框
- **分节换页** — 主要章节自动分页
- **样式代码块** — JSON schema模板以深色等宽主题渲染

---

## 质量门控

- **抓取限制：** 每次审计最多50页（质量优先于数量）
- **超时：** 每页抓取最长30秒
- **请求频率限制：** 请求间隔至少1秒，最多5个并发
- **robots.txt：** 始终遵守并检查
- **重复检测：** 跳过内容相似度>80%的页面

---

## 快速入门示例

```
# 对网站进行完整GEO审计
/geo audit https://example.com

# 检查AI爬虫能否抓取您的网站
/geo crawlers https://example.com

# 为特定页面评分AI可引用性
/geo citability https://example.com/blog/best-article

# 为网站生成llms.txt文件
/geo llmstxt https://example.com

# 获取60秒可见性快照
/geo quick https://example.com

# 生成客户可用报告
/geo report https://example.com
```
