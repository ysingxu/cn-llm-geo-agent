#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# 中国LLM GEO-SEO Claude Code Skill 安装程序 — Windows (Git Bash)
# 请在 Git Bash 中运行此脚本，不要使用 PowerShell 或 CMD。
# ============================================================

REPO_URL="https://github.com/ysingxu/cn-llm-geo-agent.git"
CLAUDE_DIR="${HOME}/.claude"
SKILLS_DIR="${CLAUDE_DIR}/skills"
AGENTS_DIR="${CLAUDE_DIR}/agents"
INSTALL_DIR="${SKILLS_DIR}/geo"
TEMP_DIR=$(mktemp -d)

INTERACTIVE=true
if [ ! -t 0 ]; then
    INTERACTIVE=false
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}+--------------------------------------------------+${NC}"
    echo -e "${BLUE}|   中国LLM GEO-SEO Claude Code Skill 安装程序    |${NC}"
    echo -e "${BLUE}|   面向：豆包 · 元宝 · DeepSeek · 文心 · 千问    |${NC}"
    echo -e "${BLUE}|   Windows / Git Bash 版本                        |${NC}"
    echo -e "${BLUE}+--------------------------------------------------+${NC}"
    echo ""
}

print_success() { echo -e "${GREEN}[OK] $1${NC}"; }
print_warning() { echo -e "${YELLOW}[!!] $1${NC}"; }
print_error()   { echo -e "${RED}[XX] $1${NC}"; }
print_info()    { echo -e "${BLUE}[>>] $1${NC}"; }

cleanup() { rm -rf "$TEMP_DIR"; }
trap cleanup EXIT

main() {
    print_header

    # ---- 检查先决条件 ----
    print_info "检查先决条件..."

    if ! command -v git &> /dev/null; then
        print_error "需要 Git 但未安装。"
        echo "  安装 Git for Windows: https://git-scm.com/downloads"
        exit 1
    fi
    print_success "Git 已找到: $(git --version)"

    PYTHON_CMD=""
    for cmd in python3 python py; do
        if command -v "$cmd" &> /dev/null; then
            _ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1 || true)
            if [ -n "$_ver" ]; then
                _major=$(echo "$_ver" | cut -d. -f1)
                _minor=$(echo "$_ver" | cut -d. -f2)
                if [ "$_major" -ge 3 ] && [ "$_minor" -ge 8 ]; then
                    PYTHON_CMD="$cmd"
                    break
                fi
            fi
        fi
    done

    if [ -z "$PYTHON_CMD" ]; then
        print_error "需要 Python 3.8+ 但未找到。"
        echo "  安装: https://www.python.org/downloads/"
        exit 1
    fi
    print_success "Python 已找到: $($PYTHON_CMD --version)"

    if ! command -v claude &> /dev/null; then
        print_warning "未在 PATH 中找到 Claude Code CLI。"
        echo "  安装: npm install -g @anthropic-ai/claude-code"
        echo ""
        if [ "$INTERACTIVE" = true ]; then
            read -r -p "仍然继续安装? (y/n): " REPLY
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi
        fi
    else
        print_success "Claude Code CLI 已找到"
    fi

    # ---- 创建目录 ----
    print_info "创建目录..."
    mkdir -p "$SKILLS_DIR" "$AGENTS_DIR" "$INSTALL_DIR" \
             "$INSTALL_DIR/scripts" "$INSTALL_DIR/schema" "$INSTALL_DIR/templates"
    print_success "目录结构已创建: $CLAUDE_DIR"

    # ---- 克隆或复制仓库 ----
    print_info "获取 GEO-SEO 技能文件..."

    SCRIPT_DIR=""
    if [ -n "${BASH_SOURCE[0]:-}" ] && [ "${BASH_SOURCE[0]}" != "bash" ]; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || true
    fi

    if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/geo/SKILL.md" ]; then
        print_info "从本地目录安装..."
        SOURCE_DIR="$SCRIPT_DIR"
    else
        print_info "从仓库克隆..."
        git clone --depth 1 "$REPO_URL" "$TEMP_DIR/repo" || {
            print_error "克隆仓库失败。请检查网络连接。"
            exit 1
        }
        SOURCE_DIR="${TEMP_DIR}/repo"
    fi

    # ---- 安装主技能 ----
    print_info "安装主 GEO 技能..."
    cp -r "$SOURCE_DIR/geo/"* "$INSTALL_DIR/"
    print_success "主技能已安装 -> ${INSTALL_DIR}/"

    # ---- 安装子技能 ----
    print_info "安装子技能..."
    SKILL_COUNT=0
    for skill_dir in "$SOURCE_DIR/skills"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            target_dir="${SKILLS_DIR}/${skill_name}"
            mkdir -p "$target_dir"
            cp -r "$skill_dir"* "$target_dir/"
            SKILL_COUNT=$((SKILL_COUNT + 1))
            print_success "  ${skill_name}"
        fi
    done
    echo "  -> 已安装 ${SKILL_COUNT} 个子技能"

    # ---- 安装代理 ----
    print_info "安装子代理..."
    AGENT_COUNT=0
    for agent_file in "$SOURCE_DIR/agents/"*.md; do
        if [ -f "$agent_file" ]; then
            cp "$agent_file" "$AGENTS_DIR/"
            AGENT_COUNT=$((AGENT_COUNT + 1))
            print_success "  $(basename "$agent_file")"
        fi
    done
    echo "  -> 已安装 ${AGENT_COUNT} 个子代理"

    # ---- 安装脚本 ----
    print_info "安装工具脚本..."
    if [ -d "$SOURCE_DIR/scripts" ]; then
        cp -r "$SOURCE_DIR/scripts/"* "$INSTALL_DIR/scripts/"
        chmod +x "$INSTALL_DIR/scripts/"*.py 2>/dev/null || true
        print_success "脚本已安装 -> ${INSTALL_DIR}/scripts/"
    fi

    # ---- 安装模板 ----
    if [ -d "$SOURCE_DIR/templates" ]; then
        cp -r "$SOURCE_DIR/templates/"* "$INSTALL_DIR/templates/"
        print_success "模板已安装 -> ${INSTALL_DIR}/templates/"
    fi

    # ---- 安装 Python 依赖 ----
    print_info "安装 Python 依赖..."
    if [ -f "$SOURCE_DIR/requirements.txt" ]; then
        $PYTHON_CMD -m pip install --user -r "$SOURCE_DIR/requirements.txt" -q 2>/dev/null && {
            print_success "Python 依赖已安装"
        } || {
            print_warning "部分 Python 依赖安装失败。"
            echo "  手动运行: $PYTHON_CMD -m pip install --user -r requirements.txt"
        }
    fi

    # ---- 验证安装 ----
    echo ""
    print_info "验证安装..."
    [ -f "$INSTALL_DIR/SKILL.md" ]  && print_success "主技能文件"   || print_error "主技能文件缺失"
    [ -d "$SKILLS_DIR/geo-audit" ]  && print_success "子技能目录"   || print_error "子技能缺失"
    [ "$(ls "$AGENTS_DIR"/geo-*.md 2>/dev/null | wc -l)" -gt 0 ] \
                                    && print_success "代理文件"     || print_error "代理文件缺失"

    # ---- 打印摘要 ----
    echo ""
    echo -e "${GREEN}+--------------------------------------------------+${NC}"
    echo -e "${GREEN}|              安装完成！                          |${NC}"
    echo -e "${GREEN}+--------------------------------------------------+${NC}"
    echo ""
    echo "  安装路径: ${INSTALL_DIR}"
    echo "  子技能:   ${SKILL_COUNT} 个"
    echo "  子代理:   ${AGENT_COUNT} 个"
    echo ""
    echo -e "${BLUE}快速入门:${NC}"
    echo "  打开 Claude Code 并尝试："
    echo ""
    echo "    /geo audit https://example.com          # 完整GEO审计"
    echo "    /geo quick https://example.com          # 60秒可见性快照"
    echo "    /geo citability https://example.com     # AI可引用性评分"
    echo "    /geo crawlers https://example.com       # AI爬虫访问检查"
    echo "    /geo platforms https://example.com      # 豆包/文心/DeepSeek优化"
    echo "    /geo brands https://example.com         # 品牌提及扫描（知乎/B站/微博）"
    echo "    /geo report https://example.com         # 生成客户报告"
    echo ""
    echo -e "${BLUE}目标平台:${NC}"
    echo "  豆包 (字节跳动) · 元宝 (腾讯混元) · DeepSeek"
    echo "  文心一言 (百度) · 通义千问 (阿里云)"
    echo ""
}

main "$@"
