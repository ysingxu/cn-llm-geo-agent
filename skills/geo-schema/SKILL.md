---
name: geo-schema
description: 面向AI可发现性优化的Schema.org结构化数据审计与生成——检测、验证并生成JSON-LD标记。针对中国AI平台增加百度结构化数据扩展检查。
version: 1.0.0
author: geo-cn
tags: [geo, schema, structured-data, json-ld, entity-recognition, ai-discoverability, china, baidu]
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write
---

# GEO结构化数据技能（中国LLM版）

## 目的

结构化数据是告诉AI系统某个实体**是什么**、做什么以及与其他实体如何关联的主要机器可读信号。在中国市场，结构化数据的重要性尤为突出——百度的知识图谱直接消费Schema.org标记，这对文心一言和百度搜索的实体识别有直接影响。

## 如何使用本技能

1. 使用 `fetch_page.py` 获取目标页面HTML
2. 检测所有现有结构化数据（JSON-LD、Microdata、RDFa）
3. 针对Schema.org规范验证检测到的schema
4. 根据业务类型识别缺失的推荐schema
5. 生成即用型JSON-LD代码块
6. 输出GEO-SCHEMA-REPORT.md

---

## 第一步：检测

**重要：** WebFetch将HTML转换为Markdown并剥离`<head>`内容，这会删除JSON-LD块。改用 `fetch_page.py`：
```bash
python3 ~/.claude/skills/geo/scripts/fetch_page.py <url> page
```

### 扫描JSON-LD
查找 `<script type="application/ld+json">` 块。一个页面可能包含多个JSON-LD块——收集所有块。

### 优先级顺序
JSON-LD是**强烈推荐的GEO格式**。百度、其他搜索引擎和AI平台都最可靠地处理JSON-LD。

---

## 第二步：验证

对每个检测到的schema块进行验证（有效JSON、有效@type、必需属性、推荐属性等）。

**中国特定验证：**
- 检查百度扩展schema属性（百度有一些非标准但被识别的扩展）
- 验证中文字段（name、description等）使用简体中文

---

## 第三步：GEO的Schema类型

### Organization（关键 — 每个企业网站必须有）
对于中国网站，`sameAs` 属性应包含中国平台URL：

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#organization",
  "name": "公司名称",
  "url": "https://example.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://example.com/logo.png"
  },
  "description": "公司一句话描述",
  "foundingDate": "2020-01-15",
  "founder": {
    "@type": "Person",
    "name": "创始人姓名"
  },
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "城市",
    "addressRegion": "省份",
    "addressCountry": "CN"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+86-xxx-xxxx-xxxx",
    "contactType": "customer service"
  },
  "sameAs": [
    "https://baike.baidu.com/item/公司名称",
    "https://www.zhihu.com/org/公司名称",
    "https://weibo.com/公司名称",
    "https://space.bilibili.com/公司账号ID",
    "https://mp.weixin.qq.com/公众号",
    "https://www.linkedin.com/company/公司名称"
  ],
  "knowsAbout": [
    "核心话题1",
    "核心话题2",
    "核心话题3"
  ]
}
```

### LocalBusiness（有实体地点的业务）

**额外推荐（中国特定）：**
- `hasMap`：指向百度地图的URL（而非Google Maps）
- 确保电话号码格式为中国格式（+86前缀）

### Article + Author（内容发布者关键）

**中国作者（Person）推荐GEO属性：**
- `sameAs`：知乎个人页面、微博账号、LinkedIn
- `jobTitle`：职称（中文）
- `worksFor`：Organization schema
- `knowsAbout`：专业领域数组
- `alumniOf`：国内大学（如适用）

### FAQPage
FAQPage schema对中国AI平台的问答提取特别有效。豆包、文心一言都会解析FAQPage结构。

### SoftwareApplication（SaaS）
同全球版本，添加中国特定属性：
- `availableLanguage`: "zh-CN"
- 应用商店链接：App Store中国区、华为应用市场、小米应用商店等

---

## 第四步：sameAs策略（中国市场关键）

对于中国市场，sameAs链接优先级：

1. **百度百科文章** — 中国AI最高权威实体链接
2. **知乎官方账号** — 元宝/腾讯权威信号
3. **微博认证账号** — 品牌实体信号
4. **B站（Bilibili）频道** — 视频内容权威
5. **微信公众号** — 腾讯/元宝生态信号
6. **LinkedIn** — 国际/企业权威（对DeepSeek和通义千问有价值）
7. **GitHub** — 技术品牌（对DeepSeek尤为重要）
8. **Wikidata条目** — 国际AI实体识别（如有）
9. **Wikipedia文章** — 国际AI最高权威（如有）
10. **行业目录** — 相关垂直目录

---

## 评分标准（0-100）

| 标准 | 分值 | 评分方式 |
|---|---|---|
| Organization/Person schema存在且完整 | 15 | 完整15分，基础10分，无则0分 |
| sameAs链接（5+中国平台） | 15 | 每个有效中国sameAs链接3分，上限15分 |
| 含作者详情的Article schema | 10 | 完整作者schema 10分，仅名字5分，无则0分 |
| 特定业务类型schema | 10 | 完整10分，部分5分，缺失0分 |
| WebSite + SearchAction | 5 | 存在5分，无则0分 |
| 内页BreadcrumbList | 5 | 存在5分，无则0分 |
| JSON-LD格式（非Microdata/RDFa） | 5 | JSON-LD 5分，混合3分，仅Microdata/RDFa 0分 |
| 服务端渲染（非JS注入） | 10 | 在HTML源码中10分，JS但在head中5分，动态JS 0分 |
| speakable属性（文章中） | 5 | 存在5分，无则0分 |
| 有效JSON + 有效Schema.org类型 | 10 | 无错误10分，轻微问题5分，重大错误0分 |
| Organization/Person中的knowsAbout | 5 | 有3+话题5分，缺失0分 |
| 无弃用schema | 5 | 干净5分，有弃用schema 0分 |

---

## 输出格式

生成 **GEO-SCHEMA-REPORT.md**：

```markdown
# GEO结构化数据报告 — [域名]
日期：[日期]
目标市场：中国

## Schema得分：XX/100

## 检测到的Schema
| 页面 | Schema类型 | 格式 | 状态 | 问题 |
|---|---|---|---|---|
| / | Organization | JSON-LD | 有效 | 缺少中国sameAs链接 |
| /blog/post-1 | Article | JSON-LD | 有效 | 无作者schema |

## 验证结果
[各schema的按属性通过/失败列表]

## 中国平台sameAs审计
| 平台 | URL | 状态 |
|---|---|---|
| 百度百科 | [URL或"未找到"] | 存在/缺失 |
| 知乎 | [URL或"未找到"] | 存在/缺失 |
| 微博 | [URL或"未找到"] | 存在/缺失 |
| B站 | [URL或"未找到"] | 存在/缺失 |
| 微信公众号 | [URL或"未找到"] | 存在/缺失 |
[继续其他推荐平台]

## 缺失的推荐Schema
[列出应存在但缺失的schema（基于业务类型）]

## 生成的JSON-LD代码
[各缺失或不完整schema的即用型JSON-LD块]

## 实施说明
- 各JSON-LD块的放置位置
- 服务端渲染要求
- 百度搜索资源平台和Schema.org验证器测试
```
