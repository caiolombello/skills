#!/usr/bin/env python3
"""Static UI lint for frontend source: accessibility defects and generic-template tells.

Dependency-free (Python 3.9+). Scans HTML, CSS, JSX/TSX, Vue, Svelte, Astro and
common template files. Heuristic by design: "error" is a near-certain defect,
"warn" a likely quality problem, "info" a signal for the design critique. It does
not replace rendering the UI (see visual_qa.mjs) or a real accessibility review.

Usage:
  python3 ui_lint.py [PATH ...] [--changed [REF]] [--format text|json] [--fail-on error|warn|never]

--changed reports only findings on lines added or modified since REF (default
HEAD) and in untracked files, so pre-existing problems do not block a change.
"""
from __future__ import annotations

import argparse
import bisect
import colorsys
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "1.0.0"
MARKUP_EXT = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".mdx", ".php",
              ".erb", ".hbs", ".njk", ".liquid", ".twig"}
SCRIPT_EXT = {".js", ".ts", ".mjs", ".cjs"}
STYLE_EXT = {".css", ".scss", ".sass", ".less", ".pcss", ".styl"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "out", ".next", ".nuxt", ".svelte-kit", ".output",
             "coverage", "vendor", ".turbo", ".vercel", ".cache", "storybook-static", "__pycache__",
             ".ui-qa", "__tests__", "__mocks__", "mocks", "fixtures", "__fixtures__", "e2e", "cypress",
             "playwright-report", "test-results", ".venv", "venv", "target"}
MAX_BYTES = 512 * 1024
SEVERITY_RANK = {"error": 0, "warn": 1, "info": 2}

CLICHES = [
    r"supercharge", r"seamless(?:ly)?", r"unlock(?:s|ing)? (?:the|your)", r"revolutioni[sz]e", r"game[- ]chang(?:er|ing)",
    r"next[- ]gen(?:eration)?", r"cutting[- ]edge", r"effortless(?:ly)?", r"elevate your", r"empower(?:s|ing)? (?:you|your|teams)",
    r"streamline your", r"unleash", r"harness the power", r"in today's fast[- ]paced", r"world[- ]class",
    r"best[- ]in[- ]class", r"all[- ]in[- ]one platform", r"blazing(?:ly)? fast", r"lightning[- ]fast",
    r"take .{1,20} to the next level", r"potencialize", r"alavanque", r"revolucion(?:e|ário|ária)",
    r"eleve (?:o|a|seu|sua)", r"transforme (?:o|a|seu|sua)", r"sem complicaç(?:ão|ões)",
    r"de forma simples e rápida", r"solução completa", r"próximo nível",
]
CLICHE_RE = re.compile(r"\b(?:" + "|".join(CLICHES) + r")\b", re.I)
PLACEHOLDER_RE = re.compile(
    r"(?i:lorem ipsum|dolor sit amet|\binsert (?:text|image|content) here\b)"
    r"|\b(?:Feature|Item|Product|Card|Title|Section) [1-9]\b|\b(?:John|Jane) Doe\b"
    r"|\b(?:Your (?:Company|Brand|Product) (?:Name|Here|Inc)|Your Logo|Company Name|Logo Here)\b")
FAKE_PROOF_RE = re.compile(
    r"\b\d+(?:[.,]\d+)?\s?[kKmM]\+?\s+(?:users|customers|developers|teams|companies|downloads|clientes|usuários|empresas)\b"
    r"|\btrusted by\b|\bconfiad[oa] por\b|★{4,}|⭐{3,}|\b99\.9+%\s*(?:uptime|disponibilidade)\b", re.I)
# Characters that render as color emoji (excludes ©, ®, ™, arrows, check marks).
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F02F\U0001F0A0-\U0001F0FF☀-⛿⭐⭕⌚⌛⏩-⏳✅✨❌❎❓-❕❗➕-➗]")
UTILITY_TOKEN = re.compile(
    r"!?(?:[\w\[\]&=:-]+:)*-?(?:(?:flex|grid|block|inline|inline-flex|inline-block|hidden|relative|absolute|fixed|sticky|"
    r"uppercase|lowercase|capitalize|truncate|container|sr-only|underline|italic|antialiased|transition|shadow|rounded|border)"
    r"|(?:p[trblxyse]?|m[trblxyse]?|gap(?:-[xy])?|space-[xy]|text|bg|rounded(?:-[trblse]{1,2})?|shadow|border(?:-[trblxy])?|"
    r"outline|ring(?:-offset)?|transition|duration|ease|delay|w|h|size|min-w|min-h|max-w|max-h|items|justify|content|self|place|"
    r"font|leading|tracking|z|top|left|right|bottom|inset(?:-[xy])?|opacity|from|via|to|animate|cursor|grid-cols|grid-rows|col-span|"
    r"row-span|overflow(?:-[xy])?|object|aspect|fill|stroke|decoration|divide(?:-[xy])?|basis|grow|shrink|order|scale|rotate|"
    r"translate-[xy]|blur|backdrop-blur|line-clamp|whitespace|break|list|align|columns|bg-gradient-to|bg-linear-to)-[\w\[\]/.#%(),:-]+)")


FOCUS_REPLACEMENT = re.compile(
    r"(?:focus(?:-visible|-within)?|group-focus(?:-visible|-within)?(?:/[\w-]+)?|peer-focus(?:-visible)?(?:/[\w-]+)?"
    r"|in-focus(?:-visible)?|has-focus(?:-visible)?|has-\[\S*?focus\S*?\]"
    r"|data-\[(?:selected|highlighted|focus|focused|focus-visible|active)[^\]]*\]|data-(?:selected|highlighted|focus|focused|active)"
    r"|aria-selected|aria-\[selected[^\]]*\]):(?:ring|outline-(?!none|hidden|0)|shadow|border|bg-|underline|inset-ring|text-)")


def looks_like_classes(value: str) -> bool:
    tokens = value.split()
    if not tokens:
        return False
    hits = sum(1 for t in tokens if UTILITY_TOKEN.fullmatch(t))
    return (hits >= 2 and hits * 2 >= len(tokens)) or (len(tokens) == 1 and hits == 1)


@dataclass
class Finding:
    rule: str
    severity: str
    message: str
    fix: str
    locations: list = field(default_factory=list)
    count: int = 0

    def add(self, path: str | None, line: int | None, detail: str = "", end: int | None = None) -> None:
        self.count += 1
        if path and len(self.locations) < 400:
            self.locations.append({"path": path, "line": line, "end": end or line, "detail": detail[:120]})


class Linter:
    def __init__(self) -> None:
        self.findings: dict[str, Finding] = {}
        self.files = 0
        self.font_sizes: set[str] = set()
        self.fonts: dict[str, int] = {}
        self.has_motion = False
        self.has_reduced_motion = False
        self.has_focus_style = False
        self.raw_colors = 0
        self.arbitrary_values = 0
        self.purple_classes = 0
        self.chromatic_classes = 0
        self.outline_reset_css: list[tuple[str, int, str, int | None]] = []
        self.span_end: int | None = None  # last line of the tag or CSS rule being reported

    # ------------------------------------------------------------- reporting
    def report(self, rule: str, severity: str, message: str, fix: str, path: str | None = None,
               line: int | None = None, detail: str = "") -> None:
        if rule not in self.findings:
            self.findings[rule] = Finding(rule, severity, message, fix)
        self.findings[rule].add(path, line, detail, self.span_end)

    # ------------------------------------------------------------- scanning
    def scan(self, paths: list[Path]) -> None:
        for root in paths:
            if root.is_file():
                self.scan_file(root)
                continue
            for path in sorted(root.rglob("*")):
                if any(part in SKIP_DIRS for part in path.relative_to(root).parts[:-1]):
                    continue
                if path.is_file() and not path.is_symlink():
                    self.scan_file(path)
        self.finish()

    def scan_file(self, path: Path) -> None:
        ext = path.suffix.lower()
        name = path.name.lower()
        if ext not in MARKUP_EXT | SCRIPT_EXT | STYLE_EXT:
            return
        if re.search(r"\.(min|test|spec)\.|\.d\.ts$|\.config\.|\.map$", name):
            return
        try:
            if path.stat().st_size > MAX_BYTES:
                return
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return
        self.files += 1
        self.span_end = None
        try:
            rel = str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            rel = str(path)
        clean = strip_comments(text, ext)
        lines = LineIndex(clean)
        is_markup = ext in MARKUP_EXT or (ext in SCRIPT_EXT and re.search(r"className=|<template|html`", clean))
        story = ".stories." in name
        if ext in STYLE_EXT or ext in {".vue", ".svelte", ".astro", ".html", ".htm"}:
            self.check_css(rel, clean, lines, embedded=ext not in STYLE_EXT)
        self.check_classes(rel, clean, lines)
        self.check_motion_and_fonts(clean)
        if is_markup:
            self.check_markup(rel, clean, lines, ext)
            if not story:
                self.check_copy(rel, clean, lines)

    # ------------------------------------------------------------- CSS
    def check_css(self, rel: str, text: str, lines: "LineIndex", embedded: bool) -> None:
        css = text
        if embedded:
            blocks = [(m.start(1), m.group(1)) for m in re.finditer(r"<style[^>]*>(.*?)</style>", text, re.S | re.I)]
        else:
            blocks = [(0, css)]
        for offset, block in blocks:
            for m in re.finditer(r"([^{};]+)\{([^{}]*)\}", block):
                selector, body = m.group(1).strip(), m.group(2)
                base = offset + m.start()
                line = lines.line(base + len(m.group(1)))
                self.span_end = lines.line(base + len(m.group(0)))
                self.css_rule(rel, selector, body, line)
                self.span_end = None

    def css_rule(self, rel: str, selector: str, body: str, line: int) -> None:
        decls = dict((k.strip().lower(), v.strip()) for k, v in re.findall(r"([\w-]+)\s*:\s*([^;]+)", body))
        if ":focus" in selector and any(k in decls for k in ("outline", "box-shadow", "border-color", "outline-color", "border", "background", "background-color", "text-decoration")):
            if not re.fullmatch(r"(none|0)(\s*!important)?", decls.get("outline", "x")) or len(decls) > 1:
                self.has_focus_style = True
        removes = re.fullmatch(r"(none|0|0px)(\s*!important)?", decls.get("outline", "")) or decls.get("outline-style") == "none"
        if removes:
            if ":focus:not(:focus-visible)" in selector.replace(" ", ""):
                pass
            elif ":focus" in selector:
                if not any(k in decls for k in ("box-shadow", "border", "border-color", "background", "background-color", "text-decoration")):
                    self.report("outline-removed", "error", "Focus outline removed without a replacement indicator.",
                                "Keep the outline or add a :focus-visible ring (outline or box-shadow, >= 3:1 contrast).", rel, line, selector)
            else:
                self.outline_reset_css.append((rel, line, selector, self.span_end))
        for prop in ("transition", "transition-property"):
            if re.match(r"all\b", decls.get(prop, "")):
                self.report("transition-all", "info", "transition: all animates layout and color changes you did not intend.",
                            "Name the properties: transition: background-color 150ms, transform 200ms.", rel, line, selector)
        if decls.get("background-clip") == "text" or decls.get("-webkit-background-clip") == "text":
            self.report("gradient-text", "warn", "Gradient-clipped text is a generic-AI tell unless it is the brand.",
                        "Use solid text color; put emphasis in type size, weight, or a single accent.", rel, line, selector)
        for prop in ("background", "background-image"):
            value = decls.get(prop, "")
            if "gradient(" in value and is_purple_gradient(value):
                self.report("purple-gradient", "warn", "Purple/indigo/pink gradient: the most common generic-AI palette.",
                            "Derive the accent from the brand or domain; confirm the brief asks for this gradient.", rel, line, selector)
        blur = re.search(r"blur\((\d+)px\)", decls.get("filter", ""))
        if blur and int(blur.group(1)) >= 40:
            self.report("glow-decoration", "info", "Heavily blurred decorative shapes (glow orbs/blobs).",
                        "Get atmosphere from imagery, texture tied to the domain, or typography instead.", rel, line, selector)
        if "backdrop-filter" in decls or "-webkit-backdrop-filter" in decls:
            self.report("glassmorphism", "info", "Glass (backdrop-filter) surface.", "Use sparingly; check text contrast over busy backgrounds.", rel, line, selector)
        size = decls.get("font-size", "")
        if size:
            self.font_sizes.add(size.replace(" ", ""))
            px = re.fullmatch(r"([\d.]+)px", size)
            rem = re.fullmatch(r"([\d.]+)rem", size)
            if (px and 0 < float(px.group(1)) < 12) or (rem and 0 < float(rem.group(1)) < 0.75):
                self.report("text-tiny", "warn", "Font size below 12px.", "Use >= 12px for UI text and >= 14-16px for running text.", rel, line, f"{selector}: {size}")
        for prop in ("height", "min-height"):
            if re.fullmatch(r"100vh", decls.get(prop, "")) and not any("dvh" in v or "svh" in v for v in decls.values()):
                self.report("viewport-height", "info", "100vh is taller than the visible area on mobile browsers.",
                            "Use min-height: 100dvh (or 100svh) with a 100vh fallback.", rel, line, selector)
        z = re.fullmatch(r"(\d+)", decls.get("z-index", ""))
        if z and int(z.group(1)) >= 100:
            self.report("z-index-scale", "info", "Large z-index values signal a missing layering scale.",
                        "Define a small z-index scale (dropdown, sticky, overlay, modal, toast).", rel, line, decls["z-index"])
        for prop, value in decls.items():
            if prop.startswith("--"):
                continue
            if re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(|\boklch\(", value) and "var(" not in value:
                self.raw_colors += 1

    # ------------------------------------------------------------- utility classes
    def check_classes(self, rel: str, text: str, lines: "LineIndex") -> None:
        # Match every literal (even empty ones) so quote pairing never drifts.
        for m in re.finditer(r"""(["'`])((?:(?!\1)[^\n\\]|\\.){0,1200}?)\1""", text):
            value = m.group(2)
            if not looks_like_classes(value):
                continue
            line = lines.line(m.start())
            tokens = value.split()
            window = text[max(0, m.start() - 400): m.end() + 1200]
            for tok in tokens:
                core = tok.split(":")[-1]
                if core in ("outline-none", "outline-hidden", "outline-0") and not tok.startswith(("dark:", "forced-colors:")):
                    if not FOCUS_REPLACEMENT.search(window):
                        # Static code cannot see wrappers or focus managers; visual_qa's focus walk is the evidence.
                        self.report("outline-removed-unverified", "warn", "Outline removed and no focus style found nearby.",
                                    "Add focus-visible:ring-2 (or an outline) here or on the wrapper, then confirm with visual_qa's focus walk.", rel, line, tok)
                if core == "transition-all":
                    self.report("transition-all", "info", "transition-all animates layout and color changes you did not intend.",
                                "Prefer transition-colors, transition-opacity, or transition-transform.", rel, line, tok)
                if core in ("h-screen", "min-h-screen"):
                    self.report("viewport-height", "info", "100vh (h-screen) is taller than the visible area on mobile browsers.",
                                "Use min-h-dvh or min-h-svh.", rel, line, tok)
                if re.fullmatch(r"z-\[(\d{3,})\]", core):
                    self.report("z-index-scale", "info", "Large z-index values signal a missing layering scale.",
                                "Define a small z-index scale in tokens.", rel, line, tok)
                if re.fullmatch(r"text-\[(?:([0-9]|1[01])px|0?\.[0-6]\d*rem)\]", core):
                    self.report("text-tiny", "warn", "Font size below 12px.", "Use >= 12px for UI text and >= 14-16px for running text.", rel, line, tok)
                if re.fullmatch(r"(?:bg|text|border|from|via|to|ring|fill|stroke|outline|decoration|shadow|divide|accent|caret)-\[(?:#|rgb|hsl|oklch)[^\]]*\]", core):
                    self.report("hardcoded-color", "warn", "Arbitrary color value bypasses the design tokens.",
                                "Add the color to the theme tokens and use the token utility.", rel, line, tok)
                elif re.fullmatch(r"[a-z-]+-\[[^\]]+\]", core):
                    self.arbitrary_values += 1
                if re.fullmatch(r"text-(?:xs|sm|base|lg|[2-9]?xl|\[[\d.]+(?:px|rem|em)\])", core):
                    self.font_sizes.add(core)
                if re.fullmatch(r"(?:bg|text|border|from|via|to|ring|fill|stroke)-(?:red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}(?:/\d+)?", core):
                    self.chromatic_classes += 1
                    if re.search(r"-(?:indigo|violet|purple|fuchsia)-", core):
                        self.purple_classes += 1
                if core.startswith(("focus:", "focus-visible:")) or tok.startswith(("focus:", "focus-visible:", "focus-within:")):
                    self.has_focus_style = True
                if re.fullmatch(r"motion-(?:safe|reduce):.*", tok) or tok.startswith(("motion-safe:", "motion-reduce:")):
                    self.has_reduced_motion = True
                if re.fullmatch(r"animate-(?!none)[\w-]+", core):
                    self.has_motion = True
            if "bg-clip-text" in tokens and "text-transparent" in tokens:
                self.report("gradient-text", "warn", "Gradient-clipped text is a generic-AI tell unless it is the brand.",
                            "Use solid text color; put emphasis in type size, weight, or a single accent.", rel, line, "bg-clip-text text-transparent")
            gradient = [t.split(":")[-1] for t in tokens if re.fullmatch(r"(?:[a-z-]+:)*(?:from|via|to)-[a-z]+-\d{2,3}(?:/\d+)?", t)]
            if any(re.match(r"(?:bg-gradient-to|bg-linear-to|bg-radial|bg-conic)", t.split(":")[-1]) for t in tokens) and gradient:
                purple = [g for g in gradient if re.search(r"-(?:indigo|violet|purple|fuchsia|pink)-", g)]
                if len(purple) * 2 >= len(gradient):
                    self.report("purple-gradient", "warn", "Purple/indigo/pink gradient: the most common generic-AI palette.",
                                "Derive the accent from the brand or domain; confirm the brief asks for this gradient.", rel, line, " ".join(gradient))
            if any(re.fullmatch(r"blur-(?:2xl|3xl|\[\d{2,}px\])", t.split(":")[-1]) for t in tokens) and any(t.split(":")[-1] in ("absolute", "fixed") for t in tokens):
                self.report("glow-decoration", "info", "Heavily blurred decorative shapes (glow orbs/blobs).",
                            "Get atmosphere from imagery, texture tied to the domain, or typography instead.", rel, line)
            if "uppercase" in tokens and any(t.split(":")[-1] in ("tracking-wide", "tracking-wider", "tracking-widest") for t in tokens):
                self.report("eyebrow-label", "info", "Small uppercase tracked label (eyebrow).", "Use eyebrows sparingly; they stop signalling hierarchy when every section has one.", rel, line)
            light_gray = [t for t in tokens if re.fullmatch(r"text-(?:gray|slate|zinc|neutral|stone)-(?:300|400)", t)]
            if light_gray and not any(re.fullmatch(r"(?:bg-(?:gray|slate|zinc|neutral|stone)-(?:7|8|9)\d{2}|bg-black)", t) for t in tokens):
                self.report("low-contrast-gray", "info", "Light gray text (300/400) is usually below 4.5:1 on light backgrounds.",
                            "Use the muted-text token (~gray-500/600 on white) and verify contrast.", rel, line, light_gray[0])

    # ------------------------------------------------------------- markup
    def check_markup(self, rel: str, text: str, lines: "LineIndex", ext: str) -> None:
        for m in re.finditer(r"<meta\b[^>]*name=[\"']viewport[\"'][^>]*>", text, re.I):
            if re.search(r"user-scalable\s*=\s*(?:no|0)|maximum-scale\s*=\s*1(?:\.0)?\b", m.group(0), re.I):
                self.report("zoom-disabled", "error", "The viewport meta blocks pinch-zoom.", "Remove user-scalable=no and maximum-scale=1.", rel, lines.line(m.start()))
        for m in re.finditer(r"userScalable\s*:\s*false|maximumScale\s*:\s*1\b", text):
            self.report("zoom-disabled", "error", "The viewport config blocks pinch-zoom.", "Remove userScalable: false and maximumScale: 1.", rel, lines.line(m.start()))
        if ext in {".html", ".htm"} and re.search(r"<html\b", text, re.I):
            html_tag = re.search(r"<html\b[^>]*>", text, re.I)
            if html_tag and not re.search(r"\blang\s*=", html_tag.group(0)):
                self.report("html-lang-missing", "warn", "<html> has no lang attribute.", 'Add lang="en" (or the page language).', rel, lines.line(html_tag.start()))
            if not re.search(r"<meta\b[^>]*name=[\"']viewport", text, re.I):
                self.report("viewport-meta-missing", "warn", "No viewport meta; phones render a zoomed-out desktop page.",
                            '<meta name="viewport" content="width=device-width, initial-scale=1">', rel, 1)
        for tag, start, attrs, inner, end in iter_tags(text, ("img", "Image")):
            self.span_end = lines.line(end)
            if "{..." in attrs:
                continue
            if not re.search(r"(?:^|[\s:])alt\b", attrs):
                self.report("img-alt-missing", "error", "Image without alt attribute.", 'Describe the image, or use alt="" when it is decorative.', rel, lines.line(start), attrs.strip()[:80])
        for tag, start, attrs, inner, end in iter_tags(text, ("div", "span", "li", "p", "td", "tr", "section", "article", "img", "svg", "i")):
            self.span_end = lines.line(end + 1 + len(inner or ""))  # through the element content
            if not re.search(r"(?:\bonClick|\bonclick|@click|v-on:click|on:click|\(click\))\s*=", attrs):
                continue
            if re.search(r"\brole\s*=", attrs) and re.search(r"\btab[iI]ndex\s*=", attrs):
                continue
            keyboard = re.search(r"onKey(?:Down|Up|Press)|onkey(?:down|up)|@key(?:down|up)|on:key(?:down|up)|\(key(?:down|up)\)", attrs)
            if keyboard and re.search(r"\brole\s*=", attrs):
                continue
            empty = inner is None or not inner.strip()
            self.report("fake-control" if not empty else "click-backdrop", "error" if not empty else "info",
                        f"Clickable <{tag}> is not keyboard or screen-reader operable." if not empty else f"Click handler on an empty <{tag}> (backdrop?).",
                        "Use <button> (actions) or <a href> (navigation); for backdrops, also close on Escape." , rel, lines.line(start), attrs.strip()[:80])
        self.span_end = None
        for m in re.finditer(r"\btab[iI]ndex\s*=\s*(?:[\"']|\{)\s*([1-9]\d*)", text):
            self.report("positive-tabindex", "error", "Positive tabindex breaks the natural focus order.", "Use tabindex 0 or -1 and fix DOM order instead.", rel, lines.line(m.start()))
        for m in re.finditer(r"\bhref\s*=\s*(?:[\"'](?:#|#!|javascript:[^\"']*)?[\"']|\{\s*[\"']#[\"']\s*\})", text):
            self.report("dead-link", "warn", "Placeholder link (href=\"#\" or javascript:).", "Link to a real destination or use a <button> for actions.", rel, lines.line(m.start()))
        for tag, start, attrs, inner, end in iter_tags(text, ("button",)):
            self.span_end = lines.line(end + 1 + len(inner or ""))  # through the element content
            if inner is None or re.search(r"aria-label(?:ledby)?\s*=|\btitle\s*=", attrs):
                continue
            visible = re.sub(r"<[^>]+>", "", inner)
            if "{" in visible:
                continue
            if not visible.strip() and re.search(r"<(?:svg\b|i\b|img\b|[A-Z][\w.]*[^>]*/>)", inner):
                self.report("icon-button-unnamed", "error", "Icon-only button without an accessible name.", 'Add aria-label="…" (and a tooltip for unfamiliar icons).', rel, lines.line(start))
        for tag, start, attrs, inner, end in iter_tags(text, ("video",)):
            self.span_end = lines.line(end)
            if re.search(r"\bauto[pP]lay\b", attrs) and not re.search(r"\bmuted\b", attrs):
                self.report("autoplay-sound", "warn", "Autoplaying video without muted.", "Add muted (and playsinline), or do not autoplay.", rel, lines.line(start))
        self.span_end = None

    # ------------------------------------------------------------- copy
    def check_copy(self, rel: str, text: str, lines: "LineIndex") -> None:
        self.span_end = None
        for offset, segment, attr in copy_segments(text):
            line = lines.line(offset)
            m = PLACEHOLDER_RE.search(segment)
            # Input placeholders may show an example value ("Jane Doe"); lorem ipsum is never fine.
            if m and (attr != "placeholder" or re.match(r"lorem|dolor", m.group(0), re.I)):
                self.report("placeholder-copy", "warn", "Placeholder content.", "Write real, domain-specific copy (or clearly labeled sample data).", rel, line, m.group(0))
            m = CLICHE_RE.search(segment)
            if m:
                self.report("cliche-copy", "info", "Generic marketing phrase.", "Replace with a concrete, product-specific claim.", rel, line, m.group(0))
            m = FAKE_PROOF_RE.search(segment)
            if m:
                self.report("unverified-proof", "info", "Social proof or metric that must be real.", "Use real, sourced numbers and names, or remove it.", rel, line, m.group(0))
            m = EMOJI_RE.search(segment)
            if m:
                self.report("emoji-ui", "warn", "Emoji in UI copy (often used as icons or bullets).", "Use icons from one set (the project's or Lucide) with consistent size and stroke.", rel, line, segment.strip()[:40])

    # ------------------------------------------------------------- project-level
    def check_motion_and_fonts(self, text: str) -> None:
        if re.search(r"@keyframes|\banimation\s*:\s*(?!none)|from ['\"](?:framer-motion|motion/react|motion|gsap)['\"]|\bmotion\.\w+", text):
            self.has_motion = True
        if re.search(r"prefers-reduced-motion|useReducedMotion|reducedMotion\s*[=:]|motion-reduce:|motion-safe:", text):
            self.has_reduced_motion = True
        families = []
        for m in re.finditer(r"(?:font-family|--font-(?!weight|size|feature|variation|display-weight)[\w-]+)\s*:\s*([^;}{\n]+)", text):
            families.append(m.group(1).split(",")[0])
        families += re.findall(r"import\s*\{([^}]+)\}\s*from\s*['\"]next/font/google['\"]", text)
        families += re.findall(r"fonts\.googleapis\.com/css2?\?family=([^&\"':]+)", text)
        families += re.findall(r"@fontsource(?:-variable)?/([\w-]+)", text)
        for raw in families:
            for name in re.split(r"[,|]", raw):
                clean = re.sub(r"[\"'+]|\bvar\(.*", " ", name).strip().replace("_", " ")
                clean = re.sub(r"\s+as\s+\w+$", "", clean)
                if clean and not clean.startswith("--") and len(clean) < 40:
                    self.fonts[clean] = self.fonts.get(clean, 0) + 1

    def finish(self) -> None:
        if self.outline_reset_css:
            severity = "warn" if self.has_focus_style else "error"
            for rel, line, selector, self.span_end in self.outline_reset_css:
                self.report("outline-removed", severity, "Outline removed in a base style; focus may be invisible.",
                            "Remove the reset or add :focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px }.", rel, line, selector)
            self.span_end = None
        if self.has_motion and not self.has_reduced_motion:
            self.report("reduced-motion-missing", "warn", "Animations exist but nothing honors prefers-reduced-motion.",
                        "Add @media (prefers-reduced-motion: reduce) overrides, motion-safe:/motion-reduce:, or useReducedMotion.")
        if len(self.font_sizes) > 10:
            self.report("type-scale-sprawl", "warn", f"{len(self.font_sizes)} distinct font sizes declared.",
                        "Collapse to a ~6-8 step type scale in tokens.", detail=", ".join(sorted(self.font_sizes))[:200])
        generic = {"inter", "roboto", "arial", "helvetica", "helvetica neue", "system-ui", "-apple-system", "sans-serif", "segoe ui", "open sans"}
        named = {f.lower() for f in self.fonts}
        if named and named <= generic:
            self.report("generic-type", "info", "Only default UI fonts are declared.",
                        "Fine for dense product UI; for brand or marketing surfaces choose a pairing from the visual direction.", detail=", ".join(sorted(self.fonts)))
        if self.chromatic_classes >= 10 and self.purple_classes * 2 >= self.chromatic_classes:
            self.report("purple-palette", "info", "Indigo/violet/purple dominate the color utilities (a common AI default).",
                        "Confirm the accent comes from the brief or brand.", detail=f"{self.purple_classes}/{self.chromatic_classes} chromatic utilities")
        if self.raw_colors > 40:
            self.report("raw-colors", "info", f"{self.raw_colors} raw color values outside custom properties.",
                        "Route colors through tokens (CSS variables / theme) so states and themes stay consistent.")
        if self.arbitrary_values > 25:
            self.report("arbitrary-values", "info", f"{self.arbitrary_values} arbitrary utility values ([13px], [37%]...).",
                        "Prefer the spacing/type scale; arbitrary values usually mean off-system sizes.")

    # ------------------------------------------------------------- output
    def results(self) -> list[Finding]:
        return sorted(self.findings.values(), key=lambda f: (SEVERITY_RANK[f.severity], -f.count, f.rule))


class LineIndex:
    def __init__(self, text: str) -> None:
        self.starts = [0] + [m.end() for m in re.finditer(r"\n", text)]

    def line(self, offset: int) -> int:
        return bisect.bisect_right(self.starts, offset)


def strip_comments(text: str, ext: str) -> str:
    """Blank out comments while preserving offsets and newlines."""
    def blank(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))

    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
    if ext not in STYLE_EXT:
        text = re.sub(r"(?m)(^|[\s;{}(),])//[^\n]*", lambda m: m.group(1) + " " * (len(m.group(0)) - len(m.group(1))), text)
    return text


def iter_tags(text: str, names: tuple[str, ...]):
    """Yield (name, start, attrs, inner, end) for opening tags, tolerating JSX braces."""
    pattern = re.compile(r"(?<![\w$.])<(" + "|".join(re.escape(n) for n in names) + r")(?=[\s/>])")
    for m in pattern.finditer(text):
        i, depth, quote = m.end(), 0, None
        while i < len(text):
            ch = text[i]
            if quote:
                if ch == quote:
                    quote = None
            elif ch in "\"'`" and depth == 0:
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(0, depth - 1)
            elif ch == ">" and depth == 0:
                break
            i += 1
        attrs = text[m.end():i]
        inner = None
        if not attrs.rstrip().endswith("/"):
            close = text.find(f"</{m.group(1)}>", i)
            if close != -1 and close - i < 4000:
                inner = text[i + 1:close]
        yield m.group(1), m.start(), attrs, inner, i


def copy_segments(text: str):
    """Approximate user-visible copy: text between tags and prose-like string literals."""
    for m in re.finditer(r">([^<>{}]*[A-Za-zÀ-ÿ\U0001F300-\U0001FAFF☀-➿][^<>{}]*)<", text):
        yield m.start(1), m.group(1), ""
    for m in re.finditer(r"""(["'])((?:(?!\1)[^\n\\]|\\.){0,300}?)\1""", text):
        value = m.group(2)
        if len(value) >= 3 and "<" not in value and " " in value.strip() and not looks_like_classes(value) and not re.search(r"[{};=]|^\s*[./@]|https?:", value):
            attr = re.search(r"([\w-]+)\s*=\s*\{?\s*$", text[max(0, m.start() - 40):m.start()])
            yield m.start(2), value, attr.group(1) if attr else ""


def parse_color(token: str):
    token = token.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})(?:[0-9a-f]{2})?", token)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+).*\)", token)
    if m:
        return tuple(float(m.group(i)) / 255 for i in (1, 2, 3))
    m = re.fullmatch(r"hsla?\(\s*([\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%.*\)", token)
    if m:
        return colorsys.hls_to_rgb(float(m.group(1)) / 360, float(m.group(3)) / 100, float(m.group(2)) / 100)
    m = re.fullmatch(r"oklch\(\s*([\d.]+%?)\s+([\d.]+)\s+([\d.]+).*\)", token)
    if m:
        return ("oklch", float(m.group(2)), float(m.group(3)))
    return None


def is_purple_gradient(value: str) -> bool:
    stops = re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|oklch\([^)]*\)", value)
    hues = []
    for stop in stops:
        c = parse_color(stop)
        if c is None:
            continue
        if c[0] == "oklch":
            if c[1] > 0.08:
                hues.append(c[2] if 270 <= c[2] <= 360 else -1)
            continue
        h, l, s = colorsys.rgb_to_hls(*c)
        if s > 0.35 and 0.15 < l < 0.9:
            hues.append(h * 360 if 235 <= h * 360 <= 330 else -1)
    purple = [h for h in hues if h >= 0]
    return len(hues) >= 2 and len(purple) * 2 >= len(hues)


def render_text(linter: Linter, max_locations: int) -> str:
    results = linter.results()
    counts = {s: sum(1 for f in results if f.severity == s) for s in SEVERITY_RANK}
    out = [f"ui_lint {VERSION}: {linter.files} files · {counts['error']} error · {counts['warn']} warn · {counts['info']} info rule types"]
    for f in results:
        out.append(f"\n{f.severity.upper()} {f.rule} (×{f.count}) — {f.message}\n  fix: {f.fix}")
        for loc in f.locations[:max_locations]:
            detail = f"  {loc['detail']}" if loc["detail"] else ""
            out.append(f"  {loc['path']}:{loc['line']}{detail}")
        if len(f.locations) > max_locations:
            out.append(f"  … {len(f.locations) - max_locations} more")
    sizes = len(linter.font_sizes)
    fonts = ", ".join(sorted(linter.fonts)) or "none declared"
    out.append(f"\nSignals: {sizes} distinct font sizes · fonts: {fonts} · {linter.raw_colors} raw colors outside tokens · {linter.arbitrary_values} arbitrary utility values")
    return "\n".join(out)


def changed_lines(ref: str) -> dict[Path, set[int] | None] | str | None:
    """Lines added or modified since ref per file (None = whole untracked file), or None outside git."""
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout
    try:
        top = Path(git("rev-parse", "--show-toplevel").strip())
        if ref == "HEAD" and subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], capture_output=True).returncode:
            return "all"  # no commits yet: everything is new
        diff = git("diff", "-U0", "--no-color", "--no-ext-diff", "--diff-filter=ACMR", ref)
        untracked = git("ls-files", "--others", "--exclude-standard", "--full-name", ":/").splitlines()
    except (OSError, subprocess.CalledProcessError):
        return None
    changed: dict[Path, set[int] | None] = {}
    current = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = None if line[4:] == "/dev/null" else (top / line[6:]).resolve()
            if current is not None:
                changed.setdefault(current, set())
        elif line.startswith("@@") and current is not None:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            start, count = int(m.group(1)), int(m.group(2) or 1)
            changed[current].update(range(start, start + count))
    for name in untracked:
        changed[(top / name).resolve()] = None
    return changed


def keep_changed(linter: Linter, changed: dict[Path, set[int] | None]) -> int:
    """Keep findings on changed lines; return how many pre-existing locations were hidden.

    A finding counts as touched when a changed line falls inside its tag or CSS rule.
    Project-wide findings are dropped.
    """
    hidden = 0
    for rule in list(linter.findings):
        finding = linter.findings[rule]
        kept = []
        for loc in finding.locations:
            lines = changed.get(Path(loc["path"]).resolve(), set())
            first = loc["line"] or 0
            last = loc.get("end") or first
            if lines is None or any(first <= c <= last for c in lines):
                kept.append(loc)
            else:
                hidden += 1
        if kept:
            finding.locations, finding.count = kept, len(kept)
        else:
            del linter.findings[rule]
    return hidden


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Static UI lint: accessibility defects and generic-template tells.")
    parser.add_argument("paths", nargs="*", default=["."], help="files or directories (default: current directory)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--fail-on", choices=["error", "warn", "never"], default="error")
    parser.add_argument("--max-locations", type=int, default=8, help="locations shown per rule in text output")
    parser.add_argument("--changed", nargs="?", const="HEAD", metavar="REF",
                        help="only report findings in files changed since REF (default HEAD) and untracked files")
    args = parser.parse_args(argv)
    paths = [Path(p) for p in args.paths]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        print(f"ui_lint: path not found: {', '.join(missing)}", file=sys.stderr)
        return 2
    linter = Linter()
    linter.scan(paths)
    hidden = 0
    if args.changed:
        changed = changed_lines(args.changed)
        if changed is None:
            print("ui_lint: --changed needs a git work tree and a valid ref; run without --changed to lint everything", file=sys.stderr)
            return 2
        if changed != "all":
            hidden = keep_changed(linter, changed)
    results = linter.results()
    if args.format == "json":
        print(json.dumps({
            "tool": "ui_lint", "version": VERSION, "files": linter.files,
            "findings": [{"rule": f.rule, "severity": f.severity, "message": f.message, "fix": f.fix,
                          "count": f.count, "locations": f.locations} for f in results],
            "signals": {"fontSizes": sorted(linter.font_sizes), "fonts": linter.fonts, "rawColors": linter.raw_colors,
                        "arbitraryValues": linter.arbitrary_values},
            "hiddenPreexisting": hidden,
        }, indent=2, ensure_ascii=False))
    else:
        print(render_text(linter, args.max_locations))
        if hidden:
            print(f"{hidden} finding(s) on lines this change did not touch are hidden; run without --changed to list them.")
    levels = {"error": ("error",), "warn": ("error", "warn"), "never": ()}[args.fail_on]
    return 1 if any(f.severity in levels for f in results) else 0


if __name__ == "__main__":
    sys.exit(main())
