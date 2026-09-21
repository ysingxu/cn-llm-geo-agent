#!/usr/bin/env python3
"""
GEO 网站体检工具 — 本地网页版服务器
双击「双击我.command」后自动启动本文件，并打开浏览器。
仅监听本机（127.0.0.1），外部电脑无法访问。
"""

import json
import os
import re
import threading
import traceback
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import geo_check

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
ERROR_LOG = os.path.join(BASE_DIR, "错误日志.txt")
PORT_RANGE = range(8756, 8776)

SERVER = None


def log_error():
    """把完整报错写入工具文件夹里的 错误日志.txt，方便用户查看和转发。"""
    try:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write("\n══════ {} ══════\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            f.write(traceback.format_exc())
    except Exception:
        pass


def build_api_response(data, report_path):
    page = data["page"]
    if page.get("errors"):
        return {"ok": False, "errors": page["errors"]}

    robots = data["robots"]
    crawlers = []
    for tier, (names, label) in geo_check.ALL_CRAWLERS:
        crawlers.append({
            "tier": tier,
            "label": label,
            "crawler": names[0],
            "status": geo_check.crawler_status(robots, names),
        })

    detail = []
    for name, sc in data["score_detail"].items():
        m = re.search(r"满分(\d+)", name)
        mx = int(m.group(1)) if m else 100
        clean_name = re.sub(r"（满分\d+）", "", name)
        detail.append({"name": clean_name, "score": sc, "max": mx})

    return {
        "ok": True,
        "url": page.get("final_url") or data["url"],
        "domain": urlparse(data["url"]).netloc,
        "generated_at": data["generated_at"],
        "score": data["score"],
        "grade": geo_check.grade(data["score"]),
        "score_detail": detail,
        "basic": {
            "title": page.get("title"),
            "description": page.get("description"),
            "word_total": page.get("word_total") or 0,
            "cjk_chars": page.get("cjk_chars") or 0,
            "h1_count": len(page.get("h1s") or []),
            "h1s": page.get("h1s") or [],
            "internal_links": page.get("internal_links") or 0,
            "external_links": page.get("external_links") or 0,
        },
        "crawlers": crawlers,
        "tech": {
            "is_https": bool(page.get("is_https")),
            "ssr_text": data["ssr_text"],
            "ld_types": page.get("ld_types") or [],
            "security_headers": {
                h: (page.get("headers") or {}).get(h) for h in geo_check.SECURITY_HEADERS
            },
            "llms_txt": bool(data["llms"]["llms_txt"]["exists"]),
            "llms_full": bool(data["llms"]["llms_full"]["exists"]),
            "sitemap_found": bool(data["sitemap"]["found"]),
            "sitemap_count": data["sitemap"]["count"],
            "sitemap_pages": data["sitemap"]["pages"][:50],
            "robots_meta": page.get("robots_meta"),
        },
        "tips": geo_check.suggestions(data),
        "report_markdown": geo_check.build_markdown(data),
        "report_path": report_path,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # 不在窗口里打印访问日志，保持界面清爽

    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            self._route_get()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            log_error()
            try:
                self._send_json({"ok": False, "errors": [
                    "程序遇到一个内部问题：{}".format(e),
                    "详细原因已写入工具文件夹里的「错误日志.txt」，可以打开查看，或把它发给帮你维护工具的人。",
                ]}, 500)
            except Exception:
                pass

    def _route_get(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            try:
                with open(INDEX_PATH, "rb") as f:
                    body = f.read()
            except OSError:
                self._send_json({"ok": False, "errors": ["界面文件缺失：index.html"]}, 500)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path == "/api/check":
            qs = parse_qs(parsed.query)
            raw = (qs.get("url") or [""])[0].strip()
            if not raw:
                self._send_json({"ok": False, "errors": ["请先输入网址"]}, 400)
                return
            url = geo_check.normalize_url(raw)
            if not url:
                self._send_json(
                    {"ok": False, "errors": ["网址格式看起来不对，请检查后重试（直接输入域名即可，如 example.com）"]},
                    400,
                )
                return
            try:
                data = geo_check.analyze(url)
            except Exception as e:  # 兜底：任何意外错误都以友好方式返回
                self._send_json({"ok": False, "errors": ["检查过程出现意外错误：{}".format(e)]}, 500)
                return
            report_path = None
            if not data["page"].get("errors"):
                try:
                    report_path = geo_check.save_report(data)
                except OSError:
                    report_path = None
            self._send_json(build_api_response(data, report_path))
        else:
            self._send_json({"ok": False, "errors": ["Not Found"]}, 404)

    def do_POST(self):
        try:
            self._route_post()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            log_error()
            try:
                self._send_json({"ok": False, "errors": [
                    "程序遇到一个内部问题：{}".format(e),
                    "详细原因已写入工具文件夹里的「错误日志.txt」。",
                ]}, 500)
            except Exception:
                pass

    def _route_post(self):
        if urlparse(self.path).path == "/api/shutdown":
            self._send_json({"ok": True})
            if SERVER is not None:
                threading.Timer(0.3, SERVER.shutdown).start()
        else:
            self._send_json({"ok": False, "errors": ["Not Found"]}, 404)


def find_free_port():
    for port in PORT_RANGE:
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            return srv
        except OSError:
            continue
    raise RuntimeError("没有可用的端口，请关闭其他正在运行的体检工具后重试")


def main():
    global SERVER
    SERVER = find_free_port()
    port = SERVER.server_address[1]
    url = "http://127.0.0.1:{}/".format(port)
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║        GEO 网站体检工具 · 已启动 (v6)     ║")
    print("  ╚══════════════════════════════════════════╝")
    print()
    print("  浏览器没有自动打开？手动复制下面的地址到浏览器：")
    print("      {}".format(url))
    print()
    print("  · 使用期间请保持本窗口开着")
    print("  · 用完后点网页里的【退出工具】，或在本窗口按 Control+C")
    print("  · 如果页面报错，详细原因会写在工具文件夹的「错误日志.txt」里")
    print()
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        SERVER.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        SERVER.server_close()
    print()
    print("  已退出，可以关闭这个窗口。")
    try:
        input("  按回车键关闭窗口…")
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
