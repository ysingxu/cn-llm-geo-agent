#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# 中国LLM GEO-SEO Claude Code Skill 安装程序 — macOS / Linux
# ============================================================

REPO_URL="https://github.com/lejiazhang/cn-llm-geo-agent.git"
CLAUDE_DIR="${HOME}/.claude"
SKILLS_DIR="${CLAUDE_DIR}/skills"
AGENTS_DIR="${CLAUDE_DIR}/agents"
INSTALL_DIR="${SKILLS_DIR}/geo"
TEMP_DIR=$(mktemp -d)

INTERACTIVE=true
if [ ! -t 0 ]; then INTERACTIVE=false; fi

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}+--------------------------------------------------+${NC}"
    echo -e "${BLUE}|   中国LLM GEO-SEO Claude Code Skill 安装程序    |${NC}"
    echo -e "${BLUE}|   面向：豆包 · 元宝 · DeepSeek · 文心 · 千问    |${NC}"
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

    print_info "检查先决条件..."
    command -v git &>/dev/null  || { print_error "需要 Git"; exit 1; }
    print_success "Git: $(git --version)"

    PYTHON_CMD=""
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            _ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1 || true)
            [ -n "$_ver" ] && _major=$(echo "$_ver" | cut -d. -f1) || continue
            [ "$_major" -ge 3 ] && { PYTHON_CMD="$cmd"; break; }
        fi
    done
    [ -z "$PYTHON_CMD" ] && { print_error "需要 Python 3.8+"; exit 1; }
    print_success "Python: $($PYTHON_CMD --version)"

    print_info "创建目录..."
    mkdir -p "$SKILLS_DIR" "$AGENTS_DIR" "$INSTALL_DIR" \
             "$INSTALL_DIR/scripts" "$INSTALL_DIR/schema" "$INSTALL_DIR/templates"

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || SCRIPT_DIR=""

    if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/geo/SKILL.md" ]; then
        SOURCE_DIR="$SCRIPT_DIR"
        print_info "从本地目录安装..."
    else
        print_info "从仓库克隆..."
        git clone --depth 1 "$REPO_URL" "$TEMP_DIR/repo" || { print_error "克隆失败"; exit 1; }
        SOURCE_DIR="${TEMP_DIR}/repo"
    fi

    cp -r "$SOURCE_DIR/geo/"* "$INSTALL_DIR/"
    print_success "主技能已安装"

    SKILL_COUNT=0
    for skill_dir in "$SOURCE_DIR/skills"/*/; do
        [ -d "$skill_dir" ] || continue
        skill_name=$(basename "$skill_dir")
        mkdir -p "${SKILLS_DIR}/${skill_name}"
        cp -r "$skill_dir"* "${SKILLS_DIR}/${skill_name}/"
        SKILL_COUNT=$((SKILL_COUNT + 1))
    done
    print_success "子技能已安装: ${SKILL_COUNT} 个"

    AGENT_COUNT=0
    for agent_file in "$SOURCE_DIR/agents/"*.md; do
        [ -f "$agent_file" ] || continue
        cp "$agent_file" "$AGENTS_DIR/"
        AGENT_COUNT=$((AGENT_COUNT + 1))
    done
    print_success "子代理已安装: ${AGENT_COUNT} 个"

    [ -d "$SOURCE_DIR/scripts" ] && cp -r "$SOURCE_DIR/scripts/"* "$INSTALL_DIR/scripts/" \
        && chmod +x "$INSTALL_DIR/scripts/"*.py 2>/dev/null || true
    [ -d "$SOURCE_DIR/templates" ] && cp -r "$SOURCE_DIR/templates/"* "$INSTALL_DIR/templates/"

    if [ -f "$SOURCE_DIR/requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r "$SOURCE_DIR/requirements.txt" -q && \
            print_success "Python 依赖已安装" || print_warning "部分依赖安装失败"
    fi

    echo ""
    echo -e "${GREEN}安装完成！${NC}"
    echo ""
    echo "快速入门："
    echo "  /geo audit https://example.com"
    echo "  /geo platforms https://example.com   # 豆包/文心/DeepSeek分析"
    echo "  /geo brands https://example.com      # 知乎/B站/微博品牌扫描"
    echo ""
}

main "$@"
