---
name: geo-report-pdf
description: 使用pandoc + Chrome无头浏览器从GEO审计生成专业PDF报告。将GEO-AUDIT-REPORT.md转换为样式精美、客户可用的PDF，含封面页、色码得分表、严重性标签发现和90天路线图。
version: 2.0.0
author: geo-cn
tags: [geo, pdf, report, client-deliverable, professional]
allowed-tools: Read, Grep, Glob, Bash, Write
---

# GEO PDF报告生成器（pandoc流程）

## 先决条件

- **pandoc** — Windows: `winget install JohnMacFarlane.Pandoc` 或 `choco install pandoc`
- **Google Chrome** — 标准安装

## 工作流

### 第一步：检查审计报告

在当前目录查找 `GEO-AUDIT-REPORT.md`。若不存在，告知用户先运行 `/geo audit <url>`。

### 第二步：从报告提取封面元数据

从 `GEO-AUDIT-REPORT.md` 顶部读取并提取：

| 字段 | 查找位置 |
|---|---|
| `brand_name` | 第一个H1标题（"GEO审计报告："之后）|
| `domain` | 第二个加粗行（如 `**域名:** example.com`）|
| `geo_score` | 匹配 `## 整体GEO得分: XX / 100` 的行 |
| `score_label` | 该行得分后的词（如"差"、"一般"、"良好"）|
| `date` | `**审计日期:**` 行 |
| `business_type` | `**业务类型:**` 行 |
| `platform` | `**CMS:**` 行 |

### 第三步：运行pandoc

**Windows：**
```bash
pandoc GEO-AUDIT-REPORT.md \
  --to html5 \
  --standalone \
  --embed-resources \
  --template "%USERPROFILE%\.claude\skills\geo\templates\geo-report-template.html" \
  --css "%USERPROFILE%\.claude\skills\geo\templates\geo-report-style.css" \
  --metadata title="GEO审计报告 — <brand_name>" \
  --metadata brand_name="<brand_name>" \
  --metadata domain="<domain>" \
  --metadata geo_score="<geo_score>" \
  --metadata score_label="<score_label>" \
  --metadata date="<date>" \
  --metadata business_type="<business_type>" \
  -o GEO-REPORT.html
```

**Mac/Linux：**
```bash
pandoc GEO-AUDIT-REPORT.md \
  --to html5 --standalone --embed-resources \
  --template ~/.claude/skills/geo/templates/geo-report-template.html \
  --css ~/.claude/skills/geo/templates/geo-report-style.css \
  --metadata title="GEO审计报告 — <brand_name>" \
  --metadata brand_name="<brand_name>" \
  --metadata domain="<domain>" \
  --metadata geo_score="<geo_score>" \
  --metadata score_label="<score_label>" \
  --metadata date="<date>" \
  --metadata business_type="<business_type>" \
  -o GEO-REPORT.html
```

### 第四步：运行Chrome无头浏览器

**Windows：**
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" \
  --headless=new --disable-gpu --no-sandbox \
  --print-to-pdf="GEO-REPORT.pdf" \
  --print-to-pdf-no-header --no-pdf-header-footer \
  --virtual-time-budget=5000 \
  "file:///$(pwd)/GEO-REPORT.html"
```

**Mac：**
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-sandbox \
  --print-to-pdf="$(pwd)/GEO-REPORT.pdf" \
  --print-to-pdf-no-header --no-pdf-header-footer \
  --virtual-time-budget=5000 \
  "file://$(pwd)/GEO-REPORT.html"
```

### 第五步：报告完成

告知用户：
- 在当前目录生成了 `GEO-REPORT.pdf`
- 文件大小
- 可选：`start GEO-REPORT.pdf`（Windows）或 `open GEO-REPORT.pdf`（Mac）预览

## PDF包含内容

- **封面页** — 深蓝渐变，品牌名，域名，GEO得分徽章（按得分着色），审计日期，业务类型
- **得分表格** — 含 `XX/100` 的单元格自动着色：≥80绿色，≥65蓝色，≥50琥珀色，≥35橙色，<35红色
- **发现章节** — 含"严重/高/中/低"的h3标题获得严重性着色左边框标注块
- **分节换页** — 主要章节自动换页
- **代码块** — JSON schema模板以深色主题等宽字体渲染
- **中文字体支持** — 确保使用支持中文的字体（如思源黑体、微软雅黑等）

## 故障排除

| 问题 | 解决方案 |
|---|---|
| `pandoc: command not found` | 安装pandoc：`winget install JohnMacFarlane.Pandoc` |
| Chrome未找到 | 检查路径（Windows: `C:\Program Files\Google\Chrome\Application\chrome.exe`）|
| PDF为空 | 将 `--virtual-time-budget` 增加到8000 |
| 封面元数据缺失 | 检查GEO-AUDIT-REPORT.md是否有标准头部格式 |
| 中文字符显示为方框 | 安装思源黑体或确保系统中文字体可用 |
