---
name: geo-update
description: 从上游仓库拉取最新的中国LLM GEO-SEO技能更新。比较已安装的文件与最新版本，显示变更内容，并就地更新所有技能、代理、脚本和Schema模板。
allowed-tools:
  - Bash
  - Read
  - Write
---

# GEO-SEO更新技能（中国LLM版）

## 目的

将本地安装的GEO-SEO技能、代理、脚本和Schema模板更新至上游仓库的最新版本。在更新前后显示变更内容摘要。

---

## 更新工作流

### 第一步：确定已安装位置

GEO-SEO工具包安装在 `~/.claude/` 下的以下位置：

| 组件 | 安装路径 |
|-----------|-------------|
| 主技能 | `~/.claude/skills/geo/` |
| 子技能 | `~/.claude/skills/geo-*/` |
| 代理 | `~/.claude/agents/geo-*.md` |
| 脚本 | `~/.claude/skills/geo/scripts/` |
| Schema模板 | `~/.claude/skills/geo/schema/` |

通过检查 `~/.claude/skills/geo/SKILL.md` 来验证安装是否存在。若不存在，告知用户GEO-SEO未安装并建议先运行安装程序。

### 第二步：从上游克隆最新版本

```bash
TEMP_DIR=$(mktemp -d)
git clone --depth 1 https://github.com/ysingxu/cn-llm-geo-agent.git "$TEMP_DIR/repo"
```

若克隆失败，报告错误并停止。不修改任何已安装文件。

### 第三步：比较已安装版本与最新版本

在复制文件前，生成差异摘要：

1. 对每个组件目录，使用 `diff --recursive --brief` 比较已安装文件与克隆文件
2. 将变更分类为：
   - **新文件** — 上游存在但本地没有
   - **已修改文件** — 两者都有但不同
   - **已删除文件** — 本地有但上游没有（不自动删除）
3. 向用户展示摘要

### 第四步：应用更新

```bash
CLAUDE_DIR="${HOME}/.claude"
SOURCE_DIR="$TEMP_DIR/repo"

# 主技能
cp -r "$SOURCE_DIR/geo/"* "$CLAUDE_DIR/skills/geo/"

# 子技能
for skill_dir in "$SOURCE_DIR/skills"/*/; do
    skill_name=$(basename "$skill_dir")
    mkdir -p "$CLAUDE_DIR/skills/${skill_name}"
    cp -r "$skill_dir"* "$CLAUDE_DIR/skills/${skill_name}/"
done

# 代理
for agent_file in "$SOURCE_DIR/agents/"*.md; do
    cp "$agent_file" "$CLAUDE_DIR/agents/"
done

# 脚本
if [ -d "$SOURCE_DIR/scripts" ]; then
    cp -r "$SOURCE_DIR/scripts/"* "$CLAUDE_DIR/skills/geo/scripts/"
    chmod +x "$CLAUDE_DIR/skills/geo/scripts/"*.py 2>/dev/null || true
fi

# Schema模板
if [ -d "$SOURCE_DIR/schema" ]; then
    cp -r "$SOURCE_DIR/schema/"* "$CLAUDE_DIR/skills/geo/schema/"
fi
```

### 第五步：更新Python依赖

```bash
python3 -m pip install -r "$SOURCE_DIR/requirements.txt" --quiet
```

### 第六步：清理

```bash
rm -rf "$TEMP_DIR"
```

### 第七步：报告结果

```
GEO-SEO更新完成（中国LLM版）
================================
新文件：      [数量]
已修改文件：  [数量]
未变更：      [数量]
上游已删除（本地保留）：[数量]

依赖：[已更新 / 未变更 / 失败]
```

---

## 重要说明

- **绝不删除上游已移除的本地安装文件**。用户可能对其进行了自定义。列出这些文件并让用户决定。
- **绝不修改 `~/.claude/settings.json` 或 `~/.claude/settings.local.json`** — 这些是用户配置文件，不是GEO-SEO工具包的一部分。
- **若已是最新版本**（无差异），报告此情况并跳过复制步骤。
- **重启提示：** 提醒用户技能变更在新的Claude Code会话中生效。他们应重启会话以使用更新的技能。
