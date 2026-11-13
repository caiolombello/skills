#!/usr/bin/env python3
"""Validate Excalidraw scene structure and basic diagram hygiene."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlparse


ALLOWED_TYPES = {
    "arrow",
    "diamond",
    "ellipse",
    "embeddable",
    "frame",
    "freedraw",
    "iframe",
    "image",
    "line",
    "magicframe",
    "rectangle",
    "text",
}
LINEAR_TYPES = {"arrow", "line"}
IMAGE_MIME = re.compile(r"^data:image/(?:png|jpeg|webp|svg\+xml);base64,", re.I)
SAFE_LINK_SCHEMES = {"", "http", "https", "mailto"}


def issue(
    issues: list[dict[str, str]],
    level: str,
    code: str,
    message: str,
    element_id: str | None = None,
) -> None:
    item = {"level": level, "code": code, "message": message}
    if element_id:
        item["element"] = element_id
    issues.append(item)


def finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def valid_points(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= 2
        and all(
            isinstance(point, list)
            and len(point) == 2
            and all(finite_number(axis) for axis in point)
            for point in value
        )
    )


def referenced_id(binding: Any) -> str | None:
    if isinstance(binding, dict):
        value = binding.get("elementId")
        return value if isinstance(value, str) and value else None
    return None


def validate_scene(scene: Any) -> tuple[list[dict[str, str]], dict[str, int]]:
    issues: list[dict[str, str]] = []
    if not isinstance(scene, dict):
        issue(issues, "error", "SCENE_TYPE", "scene root must be a JSON object")
        return issues, {"elements": 0, "active_elements": 0, "files": 0}

    if scene.get("type") != "excalidraw":
        issue(issues, "error", "SCENE_MARKER", 'scene type must be "excalidraw"')
    if not isinstance(scene.get("version"), int) or scene.get("version", 0) < 2:
        issue(issues, "error", "SCENE_VERSION", "scene version must be an integer >= 2")
    if not isinstance(scene.get("source"), str) or not scene.get("source", "").strip():
        issue(issues, "warning", "SCENE_SOURCE", "scene source is missing")

    elements = scene.get("elements")
    if not isinstance(elements, list):
        issue(issues, "error", "ELEMENTS_TYPE", "elements must be an array")
        elements = []
    app_state = scene.get("appState")
    if not isinstance(app_state, dict):
        issue(issues, "error", "APPSTATE_TYPE", "appState must be an object")
        app_state = {}
    files = scene.get("files")
    if not isinstance(files, dict):
        issue(issues, "error", "FILES_TYPE", "files must be an object")
        files = {}

    background = app_state.get("viewBackgroundColor")
    if background is not None and not isinstance(background, str):
        issue(
            issues,
            "warning",
            "BACKGROUND_TYPE",
            "appState.viewBackgroundColor should be a color string",
        )

    by_id: dict[str, dict[str, Any]] = {}
    active_ids: set[str] = set()
    geometry_keys: list[tuple[Any, ...]] = []
    image_file_ids: set[str] = set()

    for index, element in enumerate(elements):
        if not isinstance(element, dict):
            issue(
                issues,
                "error",
                "ELEMENT_TYPE",
                f"element at index {index} must be an object",
            )
            continue

        element_id = element.get("id")
        if not isinstance(element_id, str) or not element_id.strip():
            issue(
                issues,
                "error",
                "ELEMENT_ID",
                f"element at index {index} needs a non-empty string id",
            )
            continue
        if element_id in by_id:
            issue(
                issues,
                "error",
                "DUPLICATE_ID",
                "element id is duplicated",
                element_id,
            )
        by_id[element_id] = element

        deleted = bool(element.get("isDeleted", element.get("deleted", False)))
        if deleted:
            continue
        active_ids.add(element_id)

        kind = element.get("type")
        if not isinstance(kind, str):
            issue(issues, "error", "ELEMENT_KIND", "element type is missing", element_id)
        elif kind not in ALLOWED_TYPES:
            issue(
                issues,
                "warning",
                "UNKNOWN_KIND",
                f"unrecognized serialized element type: {kind}",
                element_id,
            )

        for field in ("x", "y", "width", "height"):
            value = element.get(field)
            if not finite_number(value):
                issue(
                    issues,
                    "error",
                    "GEOMETRY_NUMBER",
                    f"{field} must be a finite number",
                    element_id,
                )
        width, height = element.get("width"), element.get("height")
        if finite_number(width) and width < 0:
            issue(issues, "error", "NEGATIVE_WIDTH", "width cannot be negative", element_id)
        if finite_number(height) and height < 0:
            issue(
                issues, "error", "NEGATIVE_HEIGHT", "height cannot be negative", element_id
            )
        for field in ("x", "y", "width", "height"):
            value = element.get(field)
            if finite_number(value) and abs(value) > 10_000_000:
                issue(
                    issues,
                    "error",
                    "EXTREME_GEOMETRY",
                    f"{field} exceeds safe scene bounds",
                    element_id,
                )

        opacity = element.get("opacity")
        if opacity is not None and (
            not finite_number(opacity) or not 0 <= opacity <= 100
        ):
            issue(
                issues,
                "error",
                "OPACITY_RANGE",
                "opacity must be between 0 and 100",
                element_id,
            )

        if kind in LINEAR_TYPES and not valid_points(element.get("points")):
            issue(
                issues,
                "error",
                "LINEAR_POINTS",
                "arrow/line points must contain at least two finite [x, y] pairs",
                element_id,
            )

        if kind == "text":
            text = element.get("text")
            if not isinstance(text, str) or not text.strip():
                issue(issues, "warning", "EMPTY_TEXT", "text element is empty", element_id)
            elif "\x00" in text:
                issue(issues, "error", "TEXT_CONTROL", "text contains a NUL byte", element_id)
            font_size = element.get("fontSize")
            if not finite_number(font_size) or font_size <= 0:
                issue(
                    issues,
                    "error",
                    "FONT_SIZE",
                    "text fontSize must be a positive number",
                    element_id,
                )
            elif font_size < 14:
                issue(
                    issues,
                    "warning",
                    "SMALL_TEXT",
                    f"fontSize {font_size:g} may be unreadable at final size",
                    element_id,
                )

        if kind == "image":
            file_id = element.get("fileId")
            if not isinstance(file_id, str) or not file_id:
                issue(
                    issues,
                    "error",
                    "IMAGE_FILE_ID",
                    "image element needs a fileId",
                    element_id,
                )
            else:
                image_file_ids.add(file_id)

        link = element.get("link")
        if isinstance(link, str) and link:
            scheme = urlparse(link).scheme.lower()
            if scheme not in SAFE_LINK_SCHEMES:
                issue(
                    issues,
                    "error",
                    "UNSAFE_LINK",
                    f"link scheme is not allowed: {scheme or '(relative)'}",
                    element_id,
                )
        elif link is not None and not isinstance(link, str):
            issue(issues, "warning", "LINK_TYPE", "link should be a string", element_id)

        group_ids = element.get("groupIds")
        if group_ids is not None and (
            not isinstance(group_ids, list)
            or not all(isinstance(group_id, str) and group_id for group_id in group_ids)
        ):
            issue(
                issues,
                "error",
                "GROUP_IDS",
                "groupIds must be an array of non-empty strings",
                element_id,
            )

        if all(finite_number(element.get(field)) for field in ("x", "y", "width", "height")):
            geometry_keys.append(
                (
                    kind,
                    round(float(element["x"]), 2),
                    round(float(element["y"]), 2),
                    round(float(element["width"]), 2),
                    round(float(element["height"]), 2),
                    repr(element.get("text")),
                )
            )

    duplicate_geometries = sum(
        count - 1 for count in Counter(geometry_keys).values() if count > 1
    )
    if duplicate_geometries:
        issue(
            issues,
            "warning",
            "DUPLICATE_GEOMETRY",
            f"{duplicate_geometries} active element(s) exactly overlap an equivalent element",
        )

    for element_id in active_ids:
        element = by_id[element_id]
        refs: list[tuple[str, str | None]] = [
            ("startBinding", referenced_id(element.get("startBinding"))),
            ("endBinding", referenced_id(element.get("endBinding"))),
        ]
        for field in ("containerId", "frameId"):
            value = element.get(field)
            refs.append((field, value if isinstance(value, str) and value else None))

        for field, target_id in refs:
            raw_value = element.get(field)
            if raw_value is not None and target_id is None:
                issue(
                    issues,
                    "error",
                    "REFERENCE_SHAPE",
                    f"{field} has an invalid reference shape",
                    element_id,
                )
            elif target_id and target_id not in active_ids:
                issue(
                    issues,
                    "error",
                    "MISSING_REFERENCE",
                    f"{field} points to missing/deleted element {target_id}",
                    element_id,
                )

        bound_elements = element.get("boundElements")
        if bound_elements is None:
            continue
        if not isinstance(bound_elements, list):
            issue(
                issues,
                "error",
                "BOUND_ELEMENTS_TYPE",
                "boundElements must be an array or null",
                element_id,
            )
            continue
        seen_bound: set[str] = set()
        for bound in bound_elements:
            bound_id = bound.get("id") if isinstance(bound, dict) else None
            if not isinstance(bound_id, str) or not bound_id:
                issue(
                    issues,
                    "error",
                    "BOUND_ELEMENT_SHAPE",
                    "boundElements entry needs an id",
                    element_id,
                )
            elif bound_id not in active_ids:
                issue(
                    issues,
                    "error",
                    "BOUND_ELEMENT_MISSING",
                    f"boundElements points to missing/deleted element {bound_id}",
                    element_id,
                )
            elif bound_id in seen_bound:
                issue(
                    issues,
                    "warning",
                    "BOUND_ELEMENT_DUPLICATE",
                    f"boundElements repeats {bound_id}",
                    element_id,
                )
            else:
                seen_bound.add(bound_id)

    for element_id in active_ids:
        element = by_id[element_id]
        if element.get("type") not in LINEAR_TYPES:
            continue
        for field in ("startBinding", "endBinding"):
            target_id = referenced_id(element.get(field))
            if not target_id or target_id not in active_ids:
                continue
            target_bound = by_id[target_id].get("boundElements") or []
            reciprocal = any(
                isinstance(bound, dict) and bound.get("id") == element_id
                for bound in target_bound
            )
            if not reciprocal:
                issue(
                    issues,
                    "warning",
                    "NONRECIPROCAL_BINDING",
                    f"{field} target {target_id} does not list this element in boundElements",
                    element_id,
                )

    for file_id in sorted(image_file_ids):
        if file_id not in files:
            issue(
                issues,
                "error",
                "MISSING_FILE",
                f"image references absent files entry {file_id}",
            )
    for file_id, file_data in files.items():
        if not isinstance(file_data, dict):
            issue(issues, "error", "FILE_ENTRY", f"files[{file_id!r}] must be an object")
            continue
        data_url = file_data.get("dataURL")
        if not isinstance(data_url, str) or not IMAGE_MIME.match(data_url):
            issue(
                issues,
                "error",
                "FILE_DATA_URL",
                f"files[{file_id!r}] must contain an embedded PNG/JPEG/WebP/SVG dataURL",
            )
        elif max(0, len(data_url.partition(",")[2]) * 3 // 4) > 10 * 1024 * 1024:
            issue(
                issues,
                "warning",
                "LARGE_IMAGE",
                f"files[{file_id!r}] exceeds approximately 10 MiB",
            )
        if file_id not in image_file_ids:
            issue(
                issues,
                "warning",
                "ORPHAN_FILE",
                f"files[{file_id!r}] is not used by an active image element",
            )

    if not active_ids:
        issue(issues, "warning", "EMPTY_SCENE", "scene contains no active elements")
    elif len(active_ids) > 500:
        issue(
            issues,
            "warning",
            "LARGE_SCENE",
            f"scene has {len(active_ids)} active elements; consider progressive disclosure",
        )

    stats = {
        "elements": len(elements),
        "active_elements": len(active_ids),
        "files": len(files),
    }
    return issues, stats


def score(issues: list[dict[str, str]]) -> int:
    errors = sum(item["level"] == "error" for item in issues)
    warnings = sum(item["level"] == "warning" for item in issues)
    return max(0, 100 - errors * 20 - warnings * 3)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Excalidraw JSON structure, references, and hygiene."
    )
    parser.add_argument("file", help="input .excalidraw JSON file")
    parser.add_argument("--strict", action="store_true", help="fail on warnings too")
    parser.add_argument("--score", action="store_true", help="print a 0-100 quality score")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    path = Path(args.file)
    try:
        scene = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {path}: {exc}", file=sys.stderr)
        return 1

    issues, stats = validate_scene(scene)
    errors = sum(item["level"] == "error" for item in issues)
    warnings = sum(item["level"] == "warning" for item in issues)
    result = {
        "file": str(path),
        "stats": stats,
        "errors": errors,
        "warnings": warnings,
        "score": score(issues),
        "issues": issues,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for item in issues:
            location = f" [{item['element']}]" if item.get("element") else ""
            print(
                f"{item['level'].upper():7} {item['code']}{location}: {item['message']}"
            )
        if not issues:
            print("OK: no structural or hygiene issues found")
        print(
            f"summary: {stats['active_elements']} active elements, "
            f"{stats['files']} files, {errors} errors, {warnings} warnings"
        )
        if args.score:
            print(f"score: {result['score']}/100")

    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
