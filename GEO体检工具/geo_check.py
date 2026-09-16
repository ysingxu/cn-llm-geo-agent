#!/usr/bin/env python3
"""
GEO 网站体检工具（Mac 双击版）
纯 Python 标准库实现，无需安装任何第三方依赖。
"""

import gzip
import ipaddress
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

USE_COLOR = sys.stdout.isatty()

CHINA_CRAWLERS = [
    (["bytespider"], "豆包 / 今日头条（字节跳动）"),
    (["baiduspider"], "文心一言 / 百度"),
    (["sogou web spider", "sogouwebspider", "sogou"], "元宝 / 搜狗（腾讯）"),
    (["deepseekbot", "deepseek"], "DeepSeek"),
]
INTL_CRAWLERS = [
    (["gptbot"], "ChatGPT（OpenAI）"),
    (["claudebot"], "Claude（Anthropic）"),
    (["perplexitybot"], "Perplexity"),
    (["googlebot"], "Google 搜索"),
]
ALL_CRAWLERS = [("中国", c) for c in CHINA_CRAWLERS] + [("国际", c) for c in INTL_CRAWLERS]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
]

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def paint(text, code):
    if not USE_COLOR:
        return text
    return "\033[{}m{}\033[0m".format(code, text)


def green(t):
    return paint(t, "32")


def red(t):
    return paint(t, "31")


def yellow(t):
    return paint(t, "33")


def cyan(t):
    return paint(t, "36")


def bold(t):
    return paint(t, "1")


def dim(t):
    return paint(t, "2")


def validate_public_http_url(url):
    """Block internal/private network targets so only public http(s) URLs are fetched."""
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("网址缺少域名")
    hostname = hostname.lower()
    if hostname == "localhost" or hostname.endswith((".local", ".internal", ".lan", ".home", ".corp")):
        raise ValueError("内网主机名已拦截: {}".format(hostname))
    try:
        addrinfos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise ValueError("无法解析域名: {} ({})".format(hostname, e))
    for info in addrinfos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise ValueError("内网或保留地址已拦截: {} 解析到 {}".format(hostname, ip))


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_public_http_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http_get(url, timeout=25):
    validate_public_http_url(url)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip",
        },
    )
    opener = urllib.request.build_opener(SafeRedirectHandler)
    resp = opener.open(req, timeout=timeout)
    raw = resp.read()
    if "gzip" in (resp.headers.get("Content-Encoding") or "").lower():
        try:
            raw = gzip.decompress(raw)
        except OSError:
            pass
    charset = resp.headers.get_content_charset() or "utf-8"
    return resp, raw.decode(charset, errors="replace")


class PageParser(HTMLParser):
    JS_ROOT_RE = re.compile(r"(app|root|__next|__nuxt)", re.I)

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.metas = {}
        self.description = None
        self.canonical = None
        self.h1s = []
        self.headings = []
        self.links = []
        self.images = []
        self.ldjson = []
        self.robots_meta = None
        self.cjk_chars = 0
        self.latin_words = 0
        self.js_roots_done = []
        self._depth = 0
        self._title_buf = []
        self._in_title = False
        self._script_kind = None
        self._ld_buf = []
        self._heading = None
        self._root = None

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self._depth += 1
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = (a.get("name") or a.get("property") or "").lower()
            content = a.get("content") or ""
            if name:
                self.metas[name] = content
                if name == "description":
                    self.description = content
                if name == "robots":
                    self.robots_meta = content
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href")
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "img":
            self.images.append({"src": a.get("src", ""), "alt": a.get("alt", "")})
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading = (int(tag[1]), [])
        elif tag in ("script", "style"):
            if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
                self._script_kind = "ld"
            else:
                self._script_kind = "other"
        elif self._root is None and a.get("id") and self.JS_ROOT_RE.search(a["id"] or ""):
            self._root = {"id": a["id"], "depth": self._depth, "text_len": 0}

    def handle_data(self, data):
        if self._in_title:
            self._title_buf.append(data)
        if self._script_kind == "ld":
            self._ld_buf.append(data)
            return
        if self._script_kind == "other":
            return
        stripped = data.strip()
        if not stripped:
            return
        self.cjk_chars += len(re.findall(r"[\u4e00-\u9fff]", stripped))
        self.latin_words += len(re.findall(r"[A-Za-z0-9]+", stripped))
        if self._root is not None:
            self._root["text_len"] += len(stripped)
        if self._heading is not None:
            self._heading[1].append(data)

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self._in_title = False
            self.title = "".join(self._title_buf).strip()
            self._title_buf = []
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._heading is not None:
            level, parts = self._heading
            text = "".join(parts).strip()
            if text:
                self.headings.append((level, text))
                if level == 1:
                    self.h1s.append(text)
            self._heading = None
        if tag in ("script", "style") and self._script_kind:
            if self._script_kind == "ld" and "".join(self._ld_buf).strip():
                self.ldjson.append("".join(self._ld_buf))
            self._ld_buf = []
            self._script_kind = None
        if tag not in VOID_TAGS:
            self._depth -= 1
            if self._root is not None and self._depth < self._root["depth"]:
                self.js_roots_done.append(self._root)
                self._root = None

    def close(self):
        super().close()
        if self._root is not None:
            self.js_roots_done.append(self._root)


def fetch_page(url):
    out = {"url": url, "errors": []}
    try:
        resp, html = http_get(url)
    except ValueError as e:
        out["errors"].append("已拦截：{}".format(e))
        return out
    except urllib.error.HTTPError as e:
        out["errors"].append("网页返回错误状态：HTTP {}".format(e.code))
        return out
    except Exception as e:
        out["errors"].append("无法打开网页：{}".format(e))
        return out
    out["final_url"] = resp.geturl()
    out["status"] = resp.status
    out["headers"] = {h: resp.headers.get(h) for h in SECURITY_HEADERS}
    out["is_https"] = urlparse(resp.geturl()).scheme == "https"
    parser = PageParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as e:
        out["errors"].append("网页解析部分失败：{}".format(e))
    out["title"] = parser.title
    out["description"] = parser.description
    out["canonical"] = parser.canonical
    out["h1s"] = parser.h1s
    out["headings"] = parser.headings
    out["robots_meta"] = parser.robots_meta
    out["word_total"] = parser.cjk_chars + parser.latin_words
    out["cjk_chars"] = parser.cjk_chars
    out["js_roots"] = parser.js_roots_done
    out["links"] = parser.links
    out["images"] = parser.images
    out["ldjson_raw"] = parser.ldjson
    out["ld_types"] = []
    for raw in parser.ldjson:
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue

        def walk(node):
            if isinstance(node, dict):
                t = node.get("@type")
                if isinstance(t, str):
                    out["ld_types"].append(t)
                elif isinstance(t, list):
                    out["ld_types"].extend([x for x in t if isinstance(x, str)])
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(data)
    out["ld_types"] = sorted(set(out["ld_types"]))
    internal = 0
    external = 0
    base_netloc = urlparse(resp.geturl()).netloc
    for href in parser.links:
        absolute = urljoin(resp.geturl(), href)
        if urlparse(absolute).netloc == base_netloc:
            internal += 1
        elif urlparse(absolute).scheme in ("http", "https"):
            external += 1
    out["internal_links"] = internal
    out["external_links"] = external
    return out


def fetch_robots(url):
    parsed = urlparse(url)
    robots_url = "{}://{}/robots.txt".format(parsed.scheme, parsed.netloc)
    out = {"url": robots_url, "exists": False, "rules": {}, "sitemaps": [], "errors": []}
    try:
        resp, text = http_get(robots_url, timeout=15)
    except ValueError as e:
        out["errors"].append("已拦截：{}".format(e))
        return out
    except urllib.error.HTTPError as e:
        out["errors"].append("robots.txt 不存在（HTTP {}）".format(e.code))
        return out
    except Exception as e:
        out["errors"].append("无法获取 robots.txt：{}".format(e))
        return out
    if resp.status != 200:
        out["errors"].append("robots.txt 返回 HTTP {}".format(resp.status))
        return out
    out["exists"] = True
    current_ua = None
    for line in text.splitlines():
        line = line.strip()
        low = line.lower()
        if low.startswith("user-agent:"):
            current_ua = line.split(":", 1)[1].strip().lower()
            if current_ua and current_ua not in out["rules"]:
                out["rules"][current_ua] = []
        elif low.startswith(("disallow:", "allow:")) and current_ua:
            directive = "Disallow" if low.startswith("disallow:") else "Allow"
            path = line.split(":", 1)[1].strip()
            out["rules"][current_ua].append((directive, path))
        elif low.startswith("sitemap:"):
            sm = line.split(":", 1)[1].strip()
            if not sm.lower().startswith("http"):
                sm = "http" + sm
            out["sitemaps"].append(sm)
    return out


def crawler_status(robots, names):
    if not robots["exists"]:
        return "没有 robots.txt（默认全部允许）"
    rules = robots["rules"]
    matched = None
    for name in names:
        if name in rules:
            matched = rules[name]
            break
    if matched is None and "*" in rules:
        matched = rules["*"]
        if any(d == "Disallow" and p == "/" for d, p in matched):
            return "被通配规则屏蔽"
        return "受通配规则约束"
    if matched is None:
        return "未提及（默认允许）"
    if any(d == "Disallow" and p == "/" for d, p in matched):
        return "被屏蔽"
    if any(d == "Disallow" and p for d, p in matched):
        return "部分屏蔽"
    return "允许"


def fetch_llms_txt(url):
    parsed = urlparse(url)
    out = {}
    for key, path in (("llms_txt", "/llms.txt"), ("llms_full", "/llms-full.txt")):
        target = "{}://{}{}".format(parsed.scheme, parsed.netloc, path)
        item = {"url": target, "exists": False, "preview": ""}
        try:
            resp, text = http_get(target, timeout=15)
            if resp.status == 200:
                item["exists"] = True
                item["preview"] = "\n".join(text.splitlines()[:5])
        except Exception:
            pass
        out[key] = item
    return out


def _local(tag):
    return tag.rsplit("}", 1)[-1].lower()


def fetch_sitemap(url, robots=None):
    parsed = urlparse(url)
    out = {"found": False, "count": 0, "pages": [], "errors": []}
    candidates = list(robots["sitemaps"][:3]) if robots else []
    for path in ("/sitemap.xml", "/sitemap_index.xml"):
        candidates.append("{}://{}{}".format(parsed.scheme, parsed.netloc, path))
    seen = set()
    for sm_url in candidates:
        if sm_url in seen:
            continue
        seen.add(sm_url)
        try:
            resp, text = http_get(sm_url, timeout=15)
        except Exception:
            continue
        try:
            root = ET.fromstring(text)
        except ET.ParseError:
            continue
        if _local(root.tag) == "sitemapindex":
            child_locs = []
            for sm in root:
                if _local(sm.tag) == "sitemap":
                    for ch in sm:
                        if _local(ch.tag) == "loc" and (ch.text or "").strip():
                            child_locs.append(ch.text.strip())
            for child in child_locs[:5]:
                if len(out["pages"]) >= 500:
                    break
                try:
                    cresp, ctext = http_get(child, timeout=15)
                    croot = ET.fromstring(ctext)
                except Exception:
                    continue
                if _local(croot.tag) == "urlset":
                    out["found"] = True
                    for url_el in croot:
                        if _local(url_el.tag) == "url":
                            for ch in url_el:
                                if _local(ch.tag) == "loc" and (ch.text or "").strip():
                                    out["pages"].append(ch.text.strip())
        elif _local(root.tag) == "urlset":
            out["found"] = True
            for url_el in root:
                if _local(url_el.tag) == "url":
                    for ch in url_el:
                        if _local(ch.tag) == "loc" and (ch.text or "").strip():
                            out["pages"].append(ch.text.strip())
        if out["found"]:
            break
    out["pages"] = list(dict.fromkeys(out["pages"]))
    out["count"] = len(out["pages"])
    return out


def ssr_assessment(page):
    roots = page.get("js_roots") or []
    words = page.get("word_total") or 0
    if roots:
        for r in roots:
            if r["text_len"] < 50 and words < 200:
                return "疑似纯前端渲染（AI 爬虫可能看不到内容）", 4
    if words >= 200:
        return "服务端有内容，AI 爬虫可读取", 20
    if words == 0:
        return "页面几乎无文本内容", 4
    return "文本内容偏少", 12


def grade(score):
    if score >= 80:
        return "优秀"
    if score >= 65:
        return "良好"
    if score >= 50:
        return "一般"
    if score >= 35:
        return "待改进"
    return "需要重点优化"


def analyze(url):
    data = {"url": url, "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")}
    print(dim("  正在打开网页 …"))
    data["page"] = fetch_page(url)
    if data["page"]["errors"] and "已拦截" in data["page"]["errors"][0]:
        return data
    print(dim("  正在检查 robots.txt（AI 爬虫大门）…"))
    data["robots"] = fetch_robots(url)
    print(dim("  正在检查 llms.txt …"))
    data["llms"] = fetch_llms_txt(url)
    print(dim("  正在检查网站地图 sitemap …"))
    data["sitemap"] = fetch_sitemap(url, robots=data["robots"])

    page = data["page"]
    robots = data["robots"]

    blocked_cn = 0
    blocked_intl = 0
    for tier, (names, _) in ALL_CRAWLERS:
        status = crawler_status(robots, names)
        if "被屏蔽" in status or "被通配" in status:
            if tier == "中国":
                blocked_cn += 1
            else:
                blocked_intl += 1
    crawler_100 = max(0, 100 - blocked_cn * 20 - blocked_intl * 10 - (0 if data["sitemap"]["found"] else 10))
    ssr_text, ssr_score = ssr_assessment(page)

    ld = page.get("ld_types") or []
    if any(t in ("Organization", "LocalBusiness", "Person") for t in ld):
        sd_score = 15
    elif ld:
        sd_score = 10
    else:
        sd_score = 0

    sec_present = sum(1 for v in (page.get("headers") or {}).values() if v)
    sec_score = round(sec_present * 2.5)

    llms_score = 10 if data["llms"]["llms_txt"]["exists"] else 0
    https_score = 10 if page.get("is_https") else 0
    crawler_score = round(crawler_100 * 0.3)

    total = crawler_score + ssr_score + sd_score + sec_score + llms_score + https_score
    data["score"] = total
    data["score_detail"] = {
        "AI 爬虫访问（满分30）": crawler_score,
        "服务端内容（满分20）": ssr_score,
        "结构化数据（满分15）": sd_score,
        "安全响应头（满分15）": sec_score,
        "llms.txt（满分10）": llms_score,
        "HTTPS（满分10）": https_score,
    }
    data["ssr_text"] = ssr_text
    return data


def suggestions(data):
    tips = []
    page = data["page"]
    robots = data["robots"]
    if not page.get("is_https"):
        tips.append("启用 HTTPS：全站加密是 AI 平台与浏览器的信任基础。")
    if robots["exists"]:
        for tier, (names, label) in ALL_CRAWLERS:
            status = crawler_status(robots, names)
            if "被屏蔽" in status and tier == "中国":
                tips.append("在 robots.txt 中允许 {}（{}），否则对应 AI 平台无法引用你的内容。".format(names[0], label))
    else:
        tips.append("创建 robots.txt：明确声明允许中国 AI 爬虫（Bytespider、Baiduspider 等）。")
    if not data["llms"]["llms_txt"]["exists"]:
        tips.append("创建 llms.txt：这是帮助 AI 理解网站的新标准文件，目前仅少数网站有，是抢占先机的机会。")
    if data["score_detail"]["服务端内容（满分20）"] < 20:
        tips.append("检查服务端渲染：{}".format(data["ssr_text"]))
    if not (page.get("ld_types") or []):
        tips.append("添加 JSON-LD 结构化数据：至少包含 Organization（组织信息），帮助 AI 识别你的品牌。")
    if data["score_detail"]["安全响应头（满分15）"] < 15:
        tips.append("补充安全响应头：目前 {}/6 项，缺失的如 X-Content-Type-Options、Referrer-Policy 配置简单收益高。".format(
            sum(1 for v in page.get("headers", {}).values() if v)))
    if not data["sitemap"]["found"]:
        tips.append("创建 sitemap.xml 并在 robots.txt 中声明 Sitemap 位置。")
    if not page.get("title"):
        tips.append("补充页面 <title> 标题。")
    if not page.get("description"):
        tips.append("补充 meta description 描述。")
    h1_count = len(page.get("h1s") or [])
    if h1_count == 0:
        tips.append("添加一个 H1 主标题，且包含核心关键词。")
    elif h1_count > 1:
        tips.append("页面有 {} 个 H1，建议只保留 1 个主标题。".format(h1_count))
    no_alt = sum(1 for img in page.get("images", []) if not img.get("alt"))
    if no_alt:
        tips.append("为 {} 张无描述的图片补充 alt 文本。".format(no_alt))
    if (page.get("word_total") or 0) < 200:
        tips.append("首页文字内容偏少（{} 字），AI 引擎需要足够可引用的文本。".format(page.get("word_total") or 0))
    return tips


def print_report(data):
    page = data["page"]
    if page["errors"]:
        print()
        print(red("  ✗ 检查失败："))
        for e in page["errors"]:
            print(red("    " + e))
        return

    print()
    print(cyan("═" * 50))
    print(cyan("  网站基本信息"))
    print(cyan("═" * 50))
    print("  网址：{}".format(page.get("final_url") or page["url"]))
    print("  标题：{}".format(page.get("title") or yellow("（缺失）")))
    desc = page.get("description") or ""
    print("  描述：{}".format((desc[:60] + "…") if len(desc) > 60 else (desc or yellow("（缺失）"))))
    print("  文本量：{} 字（中文 {} 字）".format(page.get("word_total") or 0, page.get("cjk_chars") or 0))
    print("  H1 标题：{} 个".format(len(page.get("h1s") or [])))
    print("  链接：内部 {} / 外部 {}".format(page.get("internal_links") or 0, page.get("external_links") or 0))

    print()
    print(cyan("═" * 50))
    print(cyan("  AI 爬虫大门（决定 AI 能否引用你的网站）"))
    print(cyan("═" * 50))
    robots = data["robots"]
    if not robots["exists"]:
        print(yellow("  ⚠ 没有找到 robots.txt（AI 爬虫默认可以访问，但建议明确声明）"))
    for tier, (names, label) in ALL_CRAWLERS:
        status = crawler_status(robots, names)
        if "被屏蔽" in status or "被通配" in status:
            mark = red("✗ " + status)
        elif "未提及" in status or "默认" in status or "没有" in status:
            mark = green("✓ " + status)
        else:
            mark = yellow("△ " + status)
        print("  [{}] {}：{}".format(tier, label, mark))
    if robots["sitemaps"]:
        print(dim("  robots.txt 中声明的 Sitemap：{}".format(", ".join(robots["sitemaps"][:3]))))

    print()
    print(cyan("═" * 50))
    print(cyan("  技术健康"))
    print(cyan("═" * 50))
    print("  HTTPS：{}".format(green("已启用") if page.get("is_https") else red("未启用")))
    print("  服务端内容：{}".format(data["ssr_text"]))
    ld = page.get("ld_types") or []
    print("  结构化数据：{}".format(", ".join(ld) if ld else yellow("未发现 JSON-LD")))
    print("  安全响应头：{}/6 项".format(sum(1 for v in (page.get("headers") or {}).values() if v)))
    for h in SECURITY_HEADERS:
        v = (page.get("headers") or {}).get(h)
        print("    {} {}".format(green("✓") if v else red("✗"), h))
    if page.get("robots_meta"):
        print(yellow("  注意：页面 meta robots = {}（可能限制收录）".format(page["robots_meta"])))
    llms = data["llms"]
    print("  llms.txt：{}    llms-full.txt：{}".format(
        green("存在") if llms["llms_txt"]["exists"] else yellow("缺失"),
        green("存在") if llms["llms_full"]["exists"] else yellow("缺失"),
    ))
    sitemap = data["sitemap"]
    print("  网站地图：{}".format("{}（约 {} 个页面）".format(green("已找到"), sitemap["count"]) if sitemap["found"] else yellow("未找到")))

    print()
    print(cyan("═" * 50))
    print(cyan("  GEO 技术体检得分"))
    print(cyan("═" * 50))
    print(bold("  总分：{} / 100（{}）".format(data["score"], grade(data["score"]))))
    for name, sc in data["score_detail"].items():
        print("    {:<24} {:>3} 分".format(name, sc))
    tips = suggestions(data)
    if tips:
        print()
        print(cyan("═" * 50))
        print(cyan("  改进建议（按优先级）"))
        print(cyan("═" * 50))
        for i, tip in enumerate(tips[:8], 1):
            print("  {}. {}".format(i, tip))
        if len(tips) > 8:
            print(dim("  …其余 {} 条建议见报告文件".format(len(tips) - 8)))


def build_markdown(data):
    page = data["page"]
    lines = []
    lines.append("# GEO 网站体检报告")
    lines.append("")
    lines.append("- 网址：{}".format(page.get("final_url") or data["url"]))
    lines.append("- 体检时间：{}".format(data["generated_at"]))
    lines.append("- 总分：**{}/100（{}）**".format(data["score"], grade(data["score"])))
    lines.append("")
    lines.append("## 得分明细")
    lines.append("")
    lines.append("| 项目 | 得分 |")
    lines.append("|------|------|")
    for name, sc in data["score_detail"].items():
        lines.append("| {} | {} |".format(name, sc))
    lines.append("")
    lines.append("## AI 爬虫大门")
    lines.append("")
    lines.append("| 平台 | 爬虫 | 状态 |")
    lines.append("|------|------|------|")
    for tier, (names, label) in ALL_CRAWLERS:
        lines.append("| {} | {}（{}） | {} |".format(tier, label, names[0], crawler_status(data["robots"], names)))
    lines.append("")
    lines.append("## 技术健康")
    lines.append("")
    lines.append("- HTTPS：{}".format("已启用" if page.get("is_https") else "未启用"))
    lines.append("- 服务端内容：{}".format(data["ssr_text"]))
    lines.append("- 结构化数据（JSON-LD）：{}".format(", ".join(page.get("ld_types") or []) or "未发现"))
    lines.append("- 安全响应头：{}/6 项".format(sum(1 for v in (page.get("headers") or {}).values() if v)))
    for h in SECURITY_HEADERS:
        v = (page.get("headers") or {}).get(h)
        lines.append("  - {} {}: {}".format("✓" if v else "✗", h, "已配置" if v else "缺失"))
    lines.append("- llms.txt：{}".format("存在" if data["llms"]["llms_txt"]["exists"] else "缺失"))
    lines.append("- 网站地图：{}".format("{}（约{}页）".format(sitemap_count(data)) if data["sitemap"]["found"] else "未找到"))
    lines.append("")
    lines.append("## 页面基本信息")
    lines.append("")
    lines.append("- 标题：{}".format(page.get("title") or "缺失"))
    lines.append("- 描述：{}".format(page.get("description") or "缺失"))
    lines.append("- 文本量：{} 字（中文 {} 字）".format(page.get("word_total") or 0, page.get("cjk_chars") or 0))
    lines.append("- H1 标题：{}".format("；".join(page.get("h1s") or []) or "无"))
    lines.append("- 链接：内部 {} / 外部 {}".format(page.get("internal_links") or 0, page.get("external_links") or 0))
    lines.append("")
    lines.append("## 标题结构")
    lines.append("")
    for level, text in (page.get("headings") or [])[:40]:
        lines.append("{} {}".format("#" * (level + 1), text))
    lines.append("")
    lines.append("## 网站地图页面（最多列 30 个）")
    lines.append("")
    if data["sitemap"]["found"]:
        for p in data["sitemap"]["pages"][:30]:
            lines.append("- {}".format(p))
    else:
        lines.append("未找到 sitemap。")
    lines.append("")
    tips = suggestions(data)
    lines.append("## 改进建议（按优先级）")
    lines.append("")
    for i, tip in enumerate(tips, 1):
        lines.append("{}. {}".format(i, tip))
    lines.append("")
    lines.append("---")
    lines.append("*本报告由 GEO 网站体检工具（双击版）自动生成，基于公开数据的技术体检；"
                 "内容质量、品牌权威等深度分析可结合完整版工具箱使用。*")
    return "\n".join(lines) + "\n"


def sitemap_count(data):
    return data["sitemap"]["count"]


def reports_dir():
    desktop = os.path.expanduser("~/Desktop")
    if os.path.isdir(desktop):
        base = os.path.join(desktop, "GEO报告")
    else:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GEO报告")
    os.makedirs(base, exist_ok=True)
    return base


def save_report(data):
    domain = urlparse(data["url"]).netloc.replace(":", "_") or "site"
    fname = "{}-{}.md".format(re.sub(r"[^A-Za-z0-9.-]", "_", domain), datetime.now().strftime("%Y%m%d-%H%M"))
    path = os.path.join(reports_dir(), fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(build_markdown(data))
    return path


def normalize_url(s):
    s = (s or "").strip().strip('"').strip("'")
    if not s:
        return None
    if not re.match(r"^https?://", s, re.I):
        s = "https://" + s
    parsed = urlparse(s)
    if not parsed.netloc or "." not in parsed.netloc:
        return None
    return s


def ask_url():
    while True:
        try:
            raw = input(bold("\n  请输入要体检的网址（例如 example.com）: "))
        except (EOFError, KeyboardInterrupt):
            return None
        url = normalize_url(raw)
        if url:
            return url
        print(red("  网址看起来不对，请重新输入（直接输入域名即可，不用加 http）"))


MENU = """
╔══════════════════════════════════════════════╗
║          GEO 网站体检工具（双击版）          ║
║     检查网站对 AI 搜索（豆包/DeepSeek 等）    ║
║            的可见程度，并给出改进建议          ║
╚══════════════════════════════════════════════╝

  [1] 网站全面体检（推荐，约 10 秒）
  [2] 只看 AI 爬虫能不能访问我的网站
  [3] 查看网站地图（网站有哪些页面）
  [0] 退出
"""


def main():
    if os.environ.get("GEO_NO_COLOR"):
        global USE_COLOR
        USE_COLOR = False
    while True:
        print(MENU)
        try:
            choice = input(bold("  请选择功能，输入数字后回车: ")).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  再见！")
            return
        if choice == "0":
            print("  再见！报告都在「桌面/GEO报告」文件夹里。")
            return
        if choice not in ("1", "2", "3"):
            print(red("  请输入 0、1、2 或 3"))
            continue
        url = ask_url()
        if not url:
            continue
        if choice == "1":
            data = analyze(url)
            print_report(data)
            if not data["page"]["errors"] or "已拦截" not in str(data["page"]["errors"]):
                try:
                    path = save_report(data)
                    print()
                    print(green("  ✔ 报告已保存：") + path)
                except OSError as e:
                    print(yellow("  报告保存失败：{}".format(e)))
        elif choice == "2":
            print(dim("  正在检查 robots.txt（AI 爬虫大门）…"))
            robots = fetch_robots(url)
            print()
            print(cyan("═" * 50))
            print(cyan("  AI 爬虫大门 — {}".format(url)))
            print(cyan("═" * 50))
            if not robots["exists"]:
                print(yellow("  ⚠ 没有找到 robots.txt（AI 爬虫默认可以访问，但建议明确声明）"))
            for tier, (names, label) in ALL_CRAWLERS:
                status = crawler_status(robots, names)
                if "被屏蔽" in status or "被通配" in status:
                    mark = red("✗ " + status)
                elif "未提及" in status or "默认" in status or "没有" in status:
                    mark = green("✓ " + status)
                else:
                    mark = yellow("△ " + status)
                print("  [{}] {}：{}".format(tier, label, mark))
        elif choice == "3":
            print(dim("  正在检查网站地图 sitemap …"))
            sitemap = fetch_sitemap(url)
            print()
            print(cyan("═" * 50))
            print(cyan("  网站地图 — {}".format(url)))
            print(cyan("═" * 50))
            if not sitemap["found"]:
                print(yellow("  ✗ 没找到 sitemap.xml（建议创建并提交给搜索引擎）"))
            else:
                print(green("  ✓ 找到网站地图，共约 {} 个页面：".format(sitemap["count"])))
                for p in sitemap["pages"][:30]:
                    print("    - {}".format(p))
                if sitemap["count"] > 30:
                    print(dim("    … 其余 {} 个省略".format(sitemap["count"] - 30)))
        print()
        print(dim("  （提示：报告会存到 桌面/GEO报告 文件夹）"))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  已取消，再见！")
    if sys.stdout.isatty() and sys.stdin.isatty():
        try:
            input("\n按回车键关闭窗口…")
        except (EOFError, KeyboardInterrupt):
            pass
