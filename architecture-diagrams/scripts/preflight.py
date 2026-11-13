#!/usr/bin/env python3
"""Report local capabilities used by the architecture-diagrams skill."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys


SKILL_ROOT = Path(__file__).resolve().parent.parent
SHAPE_INDEX = SKILL_ROOT / "assets" / "drawio" / "shape-index.json.gz"
RENDERER = SKILL_ROOT / "assets" / "excalidraw-renderer.html"
RENDERER_BUNDLE = SKILL_ROOT / "assets" / "excalidraw-renderer.bundle.js"
RUNTIME_MANIFEST = SKILL_ROOT / "assets" / "excalidraw-runtime.json"


def executable(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    if {"drawio", "draw.io"} & set(names):
        candidates = [
            Path("/Applications/draw.io.app/Contents/MacOS/draw.io"),
            Path("/opt/drawio/drawio"),
        ]
        return next((str(path) for path in candidates if path.is_file()), None)
    return None


def module(name: str) -> str | None:
    spec = importlib.util.find_spec(name)
    return spec.origin if spec else None


def shape_count() -> tuple[bool, str]:
    if not SHAPE_INDEX.is_file():
        return False, f"missing: {SHAPE_INDEX}"
    try:
        with gzip.open(SHAPE_INDEX, "rt", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as exc:
        return False, f"unreadable: {exc}"
    return True, f"{len(data)} indexed shapes"


def runtime_integrity() -> tuple[bool, str]:
    try:
        manifest = json.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))
        actual = hashlib.sha256(RENDERER_BUNDLE.read_bytes()).hexdigest()
    except (OSError, ValueError) as exc:
        return False, f"unreadable: {exc}"
    expected = manifest.get("bundle_sha256")
    if not isinstance(expected, str) or actual != expected:
        return False, f"SHA-256 mismatch: expected {expected}, got {actual}"
    return True, f"{manifest.get('package')}@{manifest.get('package_version')} · SHA-256 OK"


def collect() -> dict[str, dict[str, object]]:
    index_ok, index_detail = shape_count()
    runtime_ok, runtime_detail = runtime_integrity()
    checks = {
        "python": {
            "ok": sys.version_info >= (3, 9),
            "detail": sys.version.split()[0],
        },
        "shape-index": {"ok": index_ok, "detail": index_detail},
        "renderer-template": {
            "ok": RENDERER.is_file(),
            "detail": str(RENDERER),
        },
        "renderer-runtime": {"ok": runtime_ok, "detail": runtime_detail},
        "drawio": {
            "ok": bool(path := executable("drawio", "draw.io")),
            "detail": path or "not found; required only for Draw.io export",
        },
        "graphviz": {
            "ok": bool(path := executable("dot")),
            "detail": path or "not found; required for autolayout and C4",
        },
        "tred": {
            "ok": bool(path := executable("tred")),
            "detail": path or "not found; Terraform reduction will be skipped",
        },
        "xvfb": {
            "ok": bool(path := executable("xvfb-run")),
            "detail": path or "not found; may be needed for Linux headless Draw.io",
        },
        "pyyaml": {
            "ok": bool(path := module("yaml")),
            "detail": path or "not found; Kubernetes JSON still works",
        },
        "playwright": {
            "ok": bool(path := module("playwright")),
            "detail": path or "not found in this Python environment",
        },
        "uv": {
            "ok": bool(path := executable("uv")),
            "detail": path or "not found",
        },
    }
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report diagram generation, validation, and export capabilities."
    )
    parser.add_argument(
        "--require",
        action="append",
        choices=["drawio", "graphviz", "excalidraw"],
        default=[],
        help="fail when the selected optional capability is unavailable",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    checks = collect()
    required = {"python", "shape-index", "renderer-template", "renderer-runtime"}
    if "drawio" in args.require:
        required.add("drawio")
    if "graphviz" in args.require:
        required.add("graphviz")
    if "excalidraw" in args.require:
        required.add("playwright")

    if args.json:
        print(json.dumps({"required": sorted(required), "checks": checks}, indent=2))
    else:
        for name, result in checks.items():
            marker = "OK" if result["ok"] else ("MISSING" if name in required else "OPTIONAL")
            print(f"{marker:8} {name:18} {result['detail']}")

    return 1 if any(not checks[name]["ok"] for name in required) else 0


if __name__ == "__main__":
    raise SystemExit(main())
