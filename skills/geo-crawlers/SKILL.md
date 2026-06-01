---
name: geo-crawlers
description: AI爬虫访问分析。检查robots.txt、meta标签和HTTP头，确定哪些AI爬虫可以访问网站。提供完整的访问图谱，以及在保持适当控制的同时最大化AI可见性的建议。专注于中国LLM平台（豆包、元宝、DeepSeek、文心一言、通义千问）及国际平台。
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
  - Write
---

# AI爬虫访问分析技能（中国LLM版）

## 目的

本技能分析网站对AI爬虫的可访问性——AI公司用来发现、索引和训练网络内容的机器人。如果AI爬虫被屏蔽，网站内容无论质量多高都无法出现在AI生成的响应中。爬虫访问是GEO的基础技术要求。

## 核心洞察

截至2026年初，许多网站无意中通过过于激进的robots.txt规则屏蔽了AI爬虫——这些规则是从旧版SEO配置继承下来的。屏蔽AI爬虫是在AI生成搜索结果中变得不可见的最快途径。对于面向中国市场的网站，还需特别注意针对国内AI平台爬虫的配置。

---

## 完整AI爬虫参考

### 一级：中国AI搜索可见性关键（建议：允许）

这些爬虫驱动着中国用户主动寻找答案的AI搜索产品。屏蔽它们直接降低在AI生成响应中的可见性。

#### 字节跳动爬虫（Bytespider / ToutiaoBot）
- **运营商：** 字节跳动
- **User-Agent：** `Bytespider`
- **完整UA字符串：** `Mozilla/5.0 (compatible; Bytespider; spider-feedback@bytedance.com) AppleWebKit/537.36`
- **用途：** 为豆包AI搜索、今日头条、抖音搜索提供内容索引。
- **屏蔽影响：** 内容不会出现在豆包AI搜索结果中，也不会被今日头条算法推荐。
- **建议：** **允许** — 豆包月活用户超1亿，屏蔽Bytespider会从最大的中国AI搜索平台之一移除内容。

#### 百度爬虫（Baiduspider）
- **运营商：** 百度
- **User-Agent：** `Baiduspider`
- **完整UA字符串：** `Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)`
- **用途：** 索引内容用于百度搜索、文心一言AI功能和百度知识图谱。
- **屏蔽影响：** 内容不会出现在百度搜索或文心一言AI回答中。百度仍是中国最大的搜索引擎。
- **建议：** **允许** — 屏蔽百度对于任何针对中国市场的网站都是致命错误。

#### 腾讯爬虫（Sogou/腾讯）
- **运营商：** 腾讯/搜狗
- **User-Agent：** `Sogou web spider`
- **用途：** 为搜狗搜索（腾讯旗下）和元宝（腾讯混元）提供内容。
- **屏蔽影响：** 内容不会出现在元宝AI回答或通过腾讯分发的搜狗结果中。
- **建议：** **允许** — 腾讯生态覆盖微信内置搜索，对内容发现至关重要。

#### 阿里巴巴爬虫（阿里/通义）
- **运营商：** 阿里巴巴
- **User-Agent：** `Qwant` / 阿里巴巴相关爬虫
- **用途：** 为通义千问和阿里巴巴搜索产品提供内容索引。
- **建议：** **允许** — 阿里巴巴生态覆盖众多电商和企业场景。

#### DeepSeek爬虫
- **运营商：** DeepSeek（深度求索）
- **User-Agent：** `DeepSeekBot` / `deepseek`
- **用途：** 为DeepSeek AI搜索和聊天功能提供内容。
- **屏蔽影响：** 内容不会出现在DeepSeek搜索结果中。DeepSeek在技术/研究领域引用量高。
- **建议：** **允许** — DeepSeek在开发者和技术用户中市场份额增长迅速。

---

### 二级：重要的国际AI生态（建议：允许）

#### GPTBot（OpenAI）
- **User-Agent：** `GPTBot`
- **用途：** ChatGPT网络浏览、搜索功能
- **建议：** **允许** — ChatGPT全球月活用户超3亿，在出口业务中尤为重要。

#### ClaudeBot（Anthropic）
- **User-Agent：** `ClaudeBot`
- **建议：** **允许** — Claude在企业和研究场景中使用广泛。

#### PerplexityBot
- **User-Agent：** `PerplexityBot`
- **建议：** **允许** — Perplexity是最好的AI搜索推荐流量来源之一。

#### Google-Extended
- **User-Agent：** `Google-Extended`
- **重要说明：** 屏蔽Google-Extended **不影响** Google搜索排名或AI概览呈现。仅控制Gemini模型训练数据使用。
- **建议：** **允许** — 屏蔽对搜索排名没有好处，可能减少Google AI功能的存在感。

#### Googlebot
- **User-Agent：** `Googlebot`
- **建议：** **允许** — 对任何希望出现在Google搜索的网站都是必须的。

---

### 三级：仅训练爬虫（根据策略决定）

#### CCBot（Common Crawl）
- **运营商：** Common Crawl（非营利）
- **建议：** **视情况而定** — 允许可增加长期AI训练存在度。屏蔽可控制训练数据使用。不影响搜索可见性。

#### anthropic-ai
- **运营商：** Anthropic（训练用）
- **建议：** **视情况而定** — 与CCBot类似。不影响Claude的实时搜索功能。

---

## 建议矩阵摘要

| 爬虫 | 级别 | 建议 | 原因 |
|---|---|---|---|
| Bytespider | 1（中国） | **允许** | 豆包（1亿+用户） |
| Baiduspider | 1（中国） | **允许** | 百度+文心一言（最大中国搜索） |
| Sogou web spider | 1（中国） | **允许** | 元宝+腾讯生态 |
| DeepSeekBot | 1（中国） | **允许** | DeepSeek AI搜索 |
| GPTBot | 2（国际） | **允许** | ChatGPT全球（3亿+用户） |
| ClaudeBot | 2（国际） | **允许** | Claude网络搜索 |
| PerplexityBot | 2（国际） | **允许** | 最佳推荐流量AI搜索 |
| Google-Extended | 2（国际） | **允许** | Gemini功能；不影响搜索排名 |
| Googlebot | 2（国际） | **允许** | Google搜索（必须） |
| CCBot | 3 | 视情况 | 仅训练数据 |
| anthropic-ai | 3 | 视情况 | 仅训练数据 |

### 最大AI可见性配置（robots.txt）

适用于希望最大化AI搜索可见性的网站：

```
# 中国AI爬虫 - 允许访问AI搜索可见性
User-agent: Bytespider
Allow: /

User-agent: Baiduspider
Allow: /

User-agent: Sogouwebspider
Allow: /

User-agent: DeepSeekBot
Allow: /

# 国际AI爬虫 - 允许
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Googlebot
Allow: /

# 传统训练爬虫 - 视情况
# User-agent: CCBot
# Disallow: /
```

---

## 分析流程

### 第一步：获取并解析robots.txt

1. 使用WebFetch获取 `[domain]/robots.txt`
2. 解析所有User-agent指令及相关Allow/Disallow规则
3. 对上述参考列表中的每个AI爬虫：
   - 检查是否有针对该爬虫的特定User-agent块
   - 检查是否有适用的通配符（`User-agent: *`）块
   - 确定有效访问权限：**允许**、**已屏蔽**或**未提及**（继承通配符规则）
4. 注意任何可能减慢AI爬虫访问的`Crawl-delay`指令
5. 检查`Sitemap`指令（AI爬虫用于发现内容）

### 第二步：检查Meta Robots标签

1. 对5-10个关键页面样本，获取HTML并检查：
   - `<meta name="robots" content="noindex">` — 屏蔽所有爬虫
   - `<meta name="robots" content="noai">` — 新兴AI使用屏蔽标签
   - `<meta name="robots" content="noimageai">` — 屏蔽AI图像训练
   - 爬虫专用meta标签
2. 记录对robots.txt指令的任何页面级覆盖

### 第三步：检查HTTP头

1. 对同一样本页面，检查响应头：
   - `X-Robots-Tag: noindex` — meta noindex的HTTP头等效物
   - `X-Robots-Tag: noai` — 屏蔽AI使用的HTTP头
2. 注意：HTTP头覆盖meta标签，且适用于非HTML资源

### 第四步：检查AI专用文件

1. 检查 `/llms.txt`（AI爬虫指导的新兴标准）
2. 检查 `/.well-known/ai-plugin.json`（OpenAI插件清单）
3. 记录每个文件的存在/缺失和质量

### 第五步：评估JavaScript渲染要求

1. 检查网站是否为SPA或严重依赖JavaScript渲染
2. 中国AI爬虫（尤其是Bytespider、百度蜘蛛）的JavaScript渲染能力有限
3. 若关键内容需要JS渲染，将其标记为潜在问题
4. 检查服务端渲染（SSR）或静态站点生成（SSG）作为缓解方案

---

## 输出格式

生成文件 `GEO-CRAWLER-ACCESS.md`：

```markdown
# AI爬虫访问报告：[域名]

**分析日期：** [日期]
**域名：** [域名]
**robots.txt状态：** [找到/未找到/错误]

---

## 爬虫访问摘要

| 爬虫 | 运营商 | 级别 | 状态 | 影响 |
|---|---|---|---|---|
| Bytespider | 字节跳动 | 1（中国） | [允许/已屏蔽/未提及] | [影响描述] |
| Baiduspider | 百度 | 1（中国） | [状态] | [影响] |
| Sogou爬虫 | 腾讯/搜狗 | 1（中国） | [状态] | [影响] |
| DeepSeekBot | DeepSeek | 1（中国） | [状态] | [影响] |
| GPTBot | OpenAI | 2（国际） | [状态] | [影响] |
| ClaudeBot | Anthropic | 2（国际） | [状态] | [影响] |
| PerplexityBot | Perplexity | 2（国际） | [状态] | [影响] |
| Google-Extended | Google | 2（国际） | [状态] | [影响] |

## AI可见性得分：[X]/100

**中国一级访问：** [X/4爬虫允许]
**国际二级访问：** [X/4爬虫允许]

---

## 严重问题

[列出任何被屏蔽的中国一级爬虫]

## 建议

### 立即行动
[所需的具体robots.txt变更]

### robots.txt推荐配置
[AI爬虫完整推荐robots.txt内容]

### 其他技术发现
- **Meta Robots标签：** [发现]
- **X-Robots-Tag头：** [发现]
- **JavaScript渲染：** [评估]
- **llms.txt：** [存在/缺失]
- **站点地图可访问性：** [评估]
```

---

## 爬虫访问评分

AI爬虫访问得分计算方式：

| 组件 | 权重 | 评分 |
|---|---|---|
| 中国一级爬虫允许 | 50% | 每个中国一级爬虫允许25分（4个=100分，缩放至50） |
| 国际二级爬虫允许 | 25% | 每个国际二级爬虫允许25分（4个=100分，缩放至25） |
| 无全面AI屏蔽 | 15% | 若无`User-agent: *` Disallow: /且无noai meta标签则满分 |
| AI专用文件存在 | 10% | llms.txt 5分，站点地图可被AI爬虫访问5分 |

最终得分 = 所有加权组件之和，上限100。
