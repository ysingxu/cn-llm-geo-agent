#!/bin/bash
# GEO 网站体检工具 启动器（双击本文件即可运行）
cd "$(dirname "$0")" || exit 1

PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        if "$cmd" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)' 2>/dev/null; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "  [!] 没有找到可用的 Python 3。"
    echo ""
    echo "      · 如果 Mac 刚弹出了安装窗口，请点击【安装】，"
    echo "        装完后再双击本文件即可。"
    echo ""
    echo "      · 如果没有弹窗，请到 https://www.python.org/downloads/mac-osx/"
    echo "        下载安装 Python 后，再双击本文件。"
    echo ""
    read -r -p "按回车键关闭窗口..." _
    exit 1
fi

"$PYTHON_CMD" server.py

echo ""
read -r -p "程序已结束，按回车键关闭窗口..." _
