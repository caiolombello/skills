#!/usr/bin/env python3
"""Render an Excalidraw scene to SVG and/or PNG with a pinned browser runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from validate_excalidraw import validate_scene


SKILL_ROOT = Path(__file__).resolve().parent.parent
RENDERER_TEMPLATE = SKILL_ROOT / "assets" / "excalidraw-renderer.html"
RENDERER_BUNDLE = SKILL_ROOT / "assets" / "excalidraw-renderer.bundle.js"
RUNTIME_MANIFEST = SKILL_ROOT / "assets" / "excalidraw-runtime.json"
BUNDLE_PLACEHOLDER = "/*__ARCHITECTURE_RENDERER_BUNDLE__*/"


def output_paths(
    input_path: Path, svg: str | None, png: str | None
) -> tuple[Path | None, Path | None]:
    if svg is None and png is None:
        return input_path.with_suffix(".svg"), None
    return (Path(svg) if svg else None, Path(png) if png else None)


def ensure_writable(
    input_path: Path, outputs: tuple[Path | None, Path | None], force: bool
) -> None:
    resolved_input = input_path.resolve()
    resolved_outputs = [output.resolve() for output in outputs if output is not None]
    if len(set(resolved_outputs)) != len(resolved_outputs):
        raise ValueError("SVG and PNG output paths must differ")
    for output in outputs:
        if output is None:
            continue
        if output.resolve() == resolved_input:
            raise ValueError("output path must differ from the editable source")
        if output.exists() and not force:
            raise FileExistsError(f"{output} exists; pass --force to overwrite it")
        output.parent.mkdir(parents=True, exist_ok=True)


def load_runtime() -> str:
    """Load the vendored renderer only when it matches the reviewed manifest."""
    try:
        manifest = json.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))
        bundle = RENDERER_BUNDLE.read_bytes()
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot load local Excalidraw runtime: {exc}") from exc
    expected = manifest.get("bundle_sha256")
    actual = hashlib.sha256(bundle).hexdigest()
    if not isinstance(expected, str) or actual != expected:
        raise RuntimeError(
            "local Excalidraw runtime integrity check failed "
            f"(expected {expected or 'missing'}, got {actual})"
        )
    return bundle.decode("utf-8")


def ensure_browser_clean(
    page_errors: list[str], network_requests: list[str], phase: str
) -> None:
    """Fail closed when the local renderer faults or attempts HTTP(S)."""
    if page_errors:
        raise RuntimeError(
            f"Excalidraw runtime browser error during {phase}: "
            + "; ".join(page_errors)
        )
    if network_requests:
        raise RuntimeError(
            f"local renderer attempted network access during {phase}: "
            + ", ".join(network_requests)
        )


def render(
    scene: dict[str, Any],
    svg_path: Path | None,
    png_path: Path | None,
    scale: float,
    padding: int,
    transparent: bool,
    timeout_seconds: float,
    browser_executable: str | None,
) -> None:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is not installed for this Python. Run with "
            "uv run --with playwright==1.62.0 python ..."
        ) from exc

    html = RENDERER_TEMPLATE.read_text(encoding="utf-8")
    if html.count(BUNDLE_PLACEHOLDER) != 1:
        raise RuntimeError("renderer template has an invalid bundle placeholder")
    html = html.replace(BUNDLE_PLACEHOLDER, load_runtime())
    timeout_ms = int(timeout_seconds * 1000)

    try:
        with sync_playwright() as playwright:
            launch_options: dict[str, Any] = {"headless": True}
            if browser_executable:
                launch_options["executable_path"] = browser_executable
            browser = playwright.chromium.launch(**launch_options)
            context = browser.new_context(device_scale_factor=scale)
            context.set_offline(True)
            page = context.new_page()
            page_errors: list[str] = []
            network_requests: list[str] = []
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.on(
                "request",
                lambda request: network_requests.append(request.url)
                if request.url.startswith(("http://", "https://"))
                else None,
            )
            page.set_default_timeout(timeout_ms)
            page.set_content(html, wait_until="domcontentloaded")
            page.wait_for_function(
                "window.architectureRendererReady === true || "
                "Boolean(window.architectureRendererError)"
            )
            runtime_error = page.evaluate("window.architectureRendererError ?? null")
            if runtime_error:
                raise RuntimeError(f"Excalidraw runtime failed to load: {runtime_error}")
            ensure_browser_clean(page_errors, network_requests, "runtime load")
            svg_text = page.evaluate(
                """async ({ scene, options }) =>
                  window.renderArchitectureScene(scene, options)""",
                {
                    "scene": scene,
                    "options": {
                        "background": not transparent,
                        "padding": padding,
                    },
                },
            )
            ensure_browser_clean(page_errors, network_requests, "scene render")

            if not isinstance(svg_text, str) or "<svg" not in svg_text:
                raise RuntimeError("renderer returned no SVG")
            if svg_path:
                svg_path.write_text(svg_text, encoding="utf-8")
            if png_path:
                page.locator("svg").screenshot(
                    path=str(png_path),
                    omit_background=transparent,
                    animations="disabled",
                )
            ensure_browser_clean(page_errors, network_requests, "export")
            browser.close()
    except PlaywrightError as exc:
        detail = str(exc)
        if "Executable doesn't exist" in detail:
            detail += (
                "\nInstall Chromium with: "
                "uv run --with playwright==1.62.0 playwright install chromium"
            )
        raise RuntimeError(detail) from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a validated .excalidraw scene to local SVG/PNG."
    )
    parser.add_argument("file", help="input .excalidraw JSON")
    parser.add_argument("--svg", help="SVG output path")
    parser.add_argument("--png", help="PNG output path")
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="PNG device scale factor, from 1 to 4 (default: 2)",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=32,
        help="export padding in scene pixels (default: 32)",
    )
    parser.add_argument(
        "--transparent",
        action="store_true",
        help="omit the scene background",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="refuse to render when validator warnings remain",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing SVG/PNG outputs",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=45.0,
        help="runtime load/render timeout in seconds (default: 45)",
    )
    parser.add_argument(
        "--browser-executable",
        help="optional local Chromium/Chrome executable",
    )
    args = parser.parse_args()

    if not 1 <= args.scale <= 4:
        parser.error("--scale must be between 1 and 4")
    if not 0 <= args.padding <= 200:
        parser.error("--padding must be between 0 and 200")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    input_path = Path(args.file)
    try:
        scene = json.loads(input_path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: cannot read {input_path}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {input_path}: {exc}", file=sys.stderr)
        return 1

    issues, _ = validate_scene(scene)
    errors = [item for item in issues if item["level"] == "error"]
    warnings = [item for item in issues if item["level"] == "warning"]
    if errors or (args.strict and warnings):
        for item in issues:
            location = f" [{item['element']}]" if item.get("element") else ""
            print(
                f"{item['level'].upper()}: {item['code']}{location}: "
                f"{item['message']}",
                file=sys.stderr,
            )
        print("error: scene validation blocks rendering", file=sys.stderr)
        return 1
    if warnings:
        print(
            f"warning: rendering with {len(warnings)} validator warning(s)",
            file=sys.stderr,
        )

    outputs = output_paths(input_path, args.svg, args.png)
    try:
        ensure_writable(input_path, outputs, args.force)
        render(
            scene,
            outputs[0],
            outputs[1],
            args.scale,
            args.padding,
            args.transparent,
            args.timeout,
            args.browser_executable,
        )
    except (FileExistsError, OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if outputs[0]:
        print(f"wrote {outputs[0]}")
    if outputs[1]:
        print(f"wrote {outputs[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
