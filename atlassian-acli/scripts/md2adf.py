#!/usr/bin/env python3
"""Convert a practical Markdown subset into an Atlassian Document Format (ADF) doc.

`acli` sends `--description`, `--description-file`, `--body` and `--body-file`
as plain text unless the content is already ADF JSON, so Markdown shows up
literally in Jira. Convert first, then pass the JSON file to acli.

Supported: ATX headings, paragraphs, hard breaks (two trailing spaces or a
trailing backslash), bullet/ordered/task lists with nesting, fenced code
blocks, blockquotes, horizontal rules, GFM pipe tables, inline code, bold,
italic, strikethrough, links, autolinks and bare http(s) URLs.

Usage:
    md2adf.py [INPUT.md|-] [-o OUTPUT.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

Node = Dict[str, object]

HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
RULE_RE = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
FENCE_RE = re.compile(r"^( *)(`{3,}|~{3,})[ \t]*([^`\s]*)[^`]*$")
LIST_RE = re.compile(r"^( *)([-*+]|\d{1,9}[.)])([ \t]+|$)(.*)$")
QUOTE_RE = re.compile(r"^ {0,3}> ?(.*)$")
TABLE_DELIM_RE = re.compile(r"^ *\|? *:?-+:? *(\| *:?-+:? *)*\|? *$")
TASK_RE = re.compile(r"^\[([ xX])\][ \t]+")
URL_RE = re.compile(r"https?://[^\s<>\]]+")
ESCAPABLE = set("\\`*_{}[]()#+-.!|~<>\"'")


# --------------------------------------------------------------------------- #
# Inline parsing
# --------------------------------------------------------------------------- #


def _text(value: str, marks: Optional[List[Node]] = None) -> Node:
    node: Node = {"type": "text", "text": value}
    if marks:
        node["marks"] = marks
    return node


def _add_mark(nodes: List[Node], mark: Node) -> List[Node]:
    for node in nodes:
        if node.get("type") != "text":
            continue
        marks = list(node.get("marks", []))  # type: ignore[arg-type]
        types = {m["type"] for m in marks}
        # ADF only allows `code` combined with `link`.
        if "code" in types and mark["type"] != "link":
            continue
        if mark["type"] == "code" and types - {"link"}:
            marks = [m for m in marks if m["type"] == "link"]
        if mark["type"] not in types:
            marks.append(mark)
        node["marks"] = marks
    return nodes


def _find_closing(src: str, delim: str, start: int) -> int:
    """Index of a closing `delim` that is not preceded by whitespace."""
    i = start
    while True:
        j = src.find(delim, i)
        if j == -1:
            return -1
        if j > start and not src[j - 1].isspace() and src[j - 1] != "\\":
            if delim[0] == "_" and j + len(delim) < len(src) and src[j + len(delim)].isalnum():
                i = j + 1
                continue
            if delim in ("*", "_") and src.startswith(delim * 2, j):
                # Skip over a nested strong delimiter.
                k = src.find(delim * 2, j + 2)
                i = (k + 2) if k != -1 else j + 2
                continue
            return j
        i = j + 1


def _find_link_end(src: str, open_bracket: int) -> Optional[Tuple[int, int, int]]:
    depth = 0
    i = open_bracket
    while i < len(src):
        ch = src[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                break
        i += 1
    else:
        return None
    close_bracket = i
    if close_bracket + 1 >= len(src) or src[close_bracket + 1] != "(":
        return None
    depth = 0
    j = close_bracket + 1
    while j < len(src):
        if src[j] == "(":
            depth += 1
        elif src[j] == ")":
            depth -= 1
            if depth == 0:
                return close_bracket, close_bracket + 2, j
        j += 1
    return None


def parse_inline(src: str) -> List[Node]:
    nodes: List[Node] = []
    buf: List[str] = []

    def flush() -> None:
        if buf:
            value = "".join(buf)
            buf.clear()
            if nodes and nodes[-1].get("type") == "text" and "marks" not in nodes[-1]:
                nodes[-1]["text"] = str(nodes[-1]["text"]) + value
            else:
                nodes.append(_text(value))

    i = 0
    n = len(src)
    while i < n:
        ch = src[i]

        if ch == "\\" and i + 1 < n and src[i + 1] in ESCAPABLE:
            buf.append(src[i + 1])
            i += 2
            continue

        if ch == "`":
            run = len(src[i:]) - len(src[i:].lstrip("`"))
            fence = "`" * run
            end = src.find(fence, i + run)
            if end != -1:
                code = src[i + run:end]
                if code.startswith(" ") and code.endswith(" ") and code.strip():
                    code = code[1:-1]
                flush()
                if code:
                    nodes.append(_text(code, [{"type": "code"}]))
                i = end + run
                continue
            buf.append(fence)
            i += run
            continue

        if ch == "<":
            end = src.find(">", i + 1)
            if end != -1 and re.fullmatch(r"https?://[^\s<>]+", src[i + 1:end]):
                url = src[i + 1:end]
                flush()
                nodes.append(_text(url, [{"type": "link", "attrs": {"href": url}}]))
                i = end + 1
                continue

        if ch == "[":
            found = _find_link_end(src, i)
            if found:
                close_bracket, url_start, url_end = found
                target = src[url_start:url_end].strip()
                href = target.split()[0].strip("<>") if target else ""
                label = parse_inline(src[i + 1:close_bracket]) or [_text(href)]
                flush()
                nodes.extend(_add_mark(label, {"type": "link", "attrs": {"href": href}}))
                i = url_end + 1
                continue

        if ch == "h" and src.startswith(("http://", "https://"), i) and (i == 0 or not src[i - 1].isalnum()):
            match = URL_RE.match(src, i)
            if match:
                url = match.group(0).rstrip(".,;:!?)'\"")
                flush()
                nodes.append(_text(url, [{"type": "link", "attrs": {"href": url}}]))
                i += len(url)
                continue

        handled = False
        for delim, mark in (("**", "strong"), ("__", "strong"), ("~~", "strike"), ("*", "em"), ("_", "em")):
            if not src.startswith(delim, i):
                continue
            after = i + len(delim)
            if after >= n or src[after].isspace():
                continue
            if delim[0] == "_" and i > 0 and src[i - 1].isalnum():
                continue  # snake_case, not emphasis
            end = _find_closing(src, delim, after)
            if end == -1:
                continue
            inner = parse_inline(src[after:end])
            flush()
            nodes.extend(_add_mark(inner, {"type": mark}))
            i = end + len(delim)
            handled = True
            break
        if handled:
            continue

        buf.append(ch)
        i += 1

    flush()
    return [node for node in nodes if node.get("type") != "text" or node.get("text")]


def parse_inline_lines(lines: List[str]) -> List[Node]:
    """Join paragraph lines; soft breaks become spaces, hard breaks become hardBreak."""
    content: List[Node] = []
    for idx, raw in enumerate(lines):
        last = idx == len(lines) - 1
        line = raw.strip() if last else raw.lstrip()
        hard = False
        if not last:
            if line.endswith("\\"):
                line, hard = line[:-1], True
            elif raw.endswith("  "):
                hard = True
            line = line.rstrip()
        content.extend(parse_inline(line))
        if not last:
            content.append({"type": "hardBreak"} if hard else _text(" "))
    merged: List[Node] = []
    for node in content:
        if (
            merged
            and node.get("type") == "text"
            and "marks" not in node
            and merged[-1].get("type") == "text"
            and "marks" not in merged[-1]
        ):
            merged[-1]["text"] = str(merged[-1]["text"]) + str(node["text"])
        else:
            merged.append(node)
    return merged


# --------------------------------------------------------------------------- #
# Block parsing
# --------------------------------------------------------------------------- #


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _expand_tabs(line: str) -> str:
    return line.expandtabs(4)


def _split_row(line: str) -> List[str]:
    row = line.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|") and not row.endswith("\\|"):
        row = row[:-1]
    cells: List[str] = []
    cur: List[str] = []
    in_code = False
    i = 0
    while i < len(row):
        ch = row[i]
        if ch == "\\" and i + 1 < len(row) and row[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def _is_table_start(lines: List[str], i: int) -> bool:
    return (
        i + 1 < len(lines)
        and "|" in lines[i]
        and bool(TABLE_DELIM_RE.match(lines[i + 1]))
        and "-" in lines[i + 1]
    )


def _starts_block(lines: List[str], i: int) -> bool:
    line = lines[i]
    return bool(
        HEADING_RE.match(line)
        or RULE_RE.match(line)
        or FENCE_RE.match(line)
        or QUOTE_RE.match(line)
        or LIST_RE.match(line) and LIST_RE.match(line).group(4).strip()  # type: ignore[union-attr]
        or _is_table_start(lines, i)
    )


def _paragraph(lines: List[str]) -> Optional[Node]:
    content = parse_inline_lines(lines)
    if not content:
        return None
    return {"type": "paragraph", "content": content}


def _cell(kind: str, text: str) -> Node:
    content = parse_inline(text)
    para: Node = {"type": "paragraph", "content": content} if content else {"type": "paragraph"}
    return {"type": kind, "attrs": {}, "content": [para]}


def parse_blocks(lines: List[str]) -> List[Node]:
    blocks: List[Node] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        fence = FENCE_RE.match(line)
        if fence:
            indent, marker, lang = len(fence.group(1)), fence.group(2), fence.group(3)
            body: List[str] = []
            i += 1
            while i < n:
                close = re.match(r"^ {0,3}(%s{%d,})[ \t]*$" % (re.escape(marker[0]), len(marker)), lines[i])
                if close:
                    i += 1
                    break
                cur = lines[i]
                body.append(cur[min(indent, _indent(cur)):])
                i += 1
            node: Node = {"type": "codeBlock", "attrs": {"language": lang} if lang else {}}
            if body:
                node["content"] = [_text("\n".join(body))]
            blocks.append(node)
            continue

        heading = HEADING_RE.match(line)
        if heading:
            content = parse_inline((heading.group(2) or "").strip())
            node = {"type": "heading", "attrs": {"level": len(heading.group(1))}}
            if content:
                node["content"] = content
            blocks.append(node)
            i += 1
            continue

        if RULE_RE.match(line):
            blocks.append({"type": "rule"})
            i += 1
            continue

        if QUOTE_RE.match(line):
            inner: List[str] = []
            while i < n and lines[i].strip():
                quote = QUOTE_RE.match(lines[i])
                if quote:
                    inner.append(quote.group(1))
                elif inner and not _starts_block(lines, i):
                    inner.append(lines[i])  # lazy continuation
                else:
                    break
                i += 1
            content = parse_blocks(inner)
            if content:
                blocks.append({"type": "blockquote", "content": content})
            continue

        if _is_table_start(lines, i):
            header = _split_row(lines[i])
            rows = [{"type": "tableRow", "content": [_cell("tableHeader", c) for c in header]}]
            i += 2
            while i < n and lines[i].strip() and "|" in lines[i]:
                cells = _split_row(lines[i])
                cells = (cells + [""] * len(header))[: len(header)]
                rows.append({"type": "tableRow", "content": [_cell("tableCell", c) for c in cells]})
                i += 1
            blocks.append({
                "type": "table",
                "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
                "content": rows,
            })
            continue

        item = LIST_RE.match(line)
        if item:
            node, i = _parse_list(lines, i)
            blocks.append(node)
            continue

        para: List[str] = [line]
        i += 1
        while i < n and lines[i].strip() and not _starts_block(lines, i):
            para.append(lines[i])
            i += 1
        paragraph = _paragraph(para)
        if paragraph:
            blocks.append(paragraph)
    return blocks


def _parse_list(lines: List[str], i: int) -> Tuple[Node, int]:
    first = LIST_RE.match(lines[i])
    assert first is not None
    base_indent = len(first.group(1))
    ordered = first.group(2)[0].isdigit()
    items: List[Node] = []
    n = len(lines)

    while i < n:
        match = LIST_RE.match(lines[i])
        if not match or len(match.group(1)) != base_indent and not (
            abs(len(match.group(1)) - base_indent) <= 1 and items
        ):
            break
        if match.group(2)[0].isdigit() != ordered:
            break
        content_col = len(match.group(1)) + len(match.group(2)) + max(1, len(match.group(3)))
        body: List[str] = [match.group(4)]
        i += 1
        while i < n:
            cur = lines[i]
            if not cur.strip():
                # Blank line: keep going only if the next non-blank line is indented under this item.
                j = i + 1
                while j < n and not lines[j].strip():
                    j += 1
                if j < n and _indent(lines[j]) > base_indent:
                    body.extend([""] * (j - i))
                    i = j
                    continue
                break
            if _indent(cur) > base_indent:
                body.append(cur[min(content_col, _indent(cur)):])
                i += 1
                continue
            if body[-1].strip() and not _starts_block(lines, i):
                body.append(cur)  # lazy paragraph continuation
                i += 1
                continue
            break

        prefix = ""
        task = TASK_RE.match(body[0])
        if task:
            prefix = "☑ " if task.group(1).lower() == "x" else "☐ "
            body[0] = body[0][task.end():]
        content = parse_blocks(body)
        if prefix:
            if content and content[0].get("type") == "paragraph":
                content[0]["content"] = [_text(prefix)] + list(content[0]["content"])  # type: ignore[arg-type]
            else:
                content.insert(0, {"type": "paragraph", "content": [_text(prefix.strip())]})
        if not content or content[0].get("type") != "paragraph":
            content.insert(0, {"type": "paragraph"})
        items.append({"type": "listItem", "content": content})

        # A blank line followed by a non-list line ends the list.
        if i < n and not lines[i].strip():
            break

    node: Node = {"type": "orderedList" if ordered else "bulletList", "content": items}
    if ordered:
        start = int(re.match(r"\d+", first.group(2)).group(0))  # type: ignore[union-attr]
        node["attrs"] = {"order": start}
    return node, i


def convert(markdown: str) -> Node:
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_expand_tabs(line.rstrip("\n")) for line in text.split("\n")]
    return {"type": "doc", "version": 1, "content": parse_blocks(lines)}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Convert Markdown to Atlassian Document Format (ADF) JSON.")
    parser.add_argument("input", nargs="?", default="-", help="Markdown file, or - for stdin (default)")
    parser.add_argument("-o", "--output", help="Write ADF JSON here instead of stdout")
    args = parser.parse_args(argv)

    source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
    doc = convert(source)
    if not doc["content"]:
        print("md2adf: input is empty; refusing to emit an empty description", file=sys.stderr)
        return 1
    payload = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
