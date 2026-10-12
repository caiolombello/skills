#!/usr/bin/env python3
"""WCAG 2.x contrast for color pairs, including oklch() tokens. Dependency-free.

Usage:
  python3 contrast.py FOREGROUND BACKGROUND [FOREGROUND BACKGROUND ...] [--min 4.5]

Colors: #rgb, #rrggbb, #rrggbbaa, rgb()/rgba(), hsl()/hsla(), oklch(L C H [/ A]),
white, black. A translucent foreground is composited over its background.
Exit status 1 when any pair is below --min (default 4.5, normal-size text).
"""
from __future__ import annotations

import argparse
import colorsys
import math
import re
import sys


def _srgb_to_linear(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(v: float) -> float:
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def _oklch_to_srgb(lightness: float, chroma: float, hue: float) -> tuple[tuple[float, float, float], bool]:
    a = chroma * math.cos(math.radians(hue))
    b = chroma * math.sin(math.radians(hue))
    l_ = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    lin = (
        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
    )
    in_gamut = all(-1e-4 <= v <= 1 + 1e-4 for v in lin)
    srgb = tuple(min(1.0, max(0.0, _linear_to_srgb(min(1.0, max(0.0, v))))) for v in lin)
    return srgb, in_gamut


def parse(value: str) -> tuple[tuple[float, float, float], float, bool]:
    """Return ((r, g, b) in 0..1 sRGB, alpha, in_gamut)."""
    v = value.strip().lower()
    named = {"white": "#ffffff", "black": "#000000"}
    v = named.get(v, v)
    m = re.fullmatch(r"#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})", v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        rgb = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        alpha = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return rgb, alpha, True
    tokens = re.findall(r"[\d.]+%?", v)
    nums = [float(x[:-1]) / 100 if x.endswith("%") else float(x) for x in tokens]
    if v.startswith("rgb") and len(nums) >= 3:
        channels = tuple(n if tokens[i].endswith("%") else n / 255 for i, n in enumerate(nums[:3]))
        return channels, nums[3] if len(nums) > 3 else 1.0, True
    if v.startswith("hsl") and len(nums) >= 3:
        hue, sat, light = nums[0], nums[1], nums[2]
        return colorsys.hls_to_rgb(hue / 360, light, sat), nums[3] if len(nums) > 3 else 1.0, True
    if v.startswith("oklch") and len(nums) >= 3:
        lightness = nums[0] if nums[0] <= 1 else nums[0] / 100
        rgb, in_gamut = _oklch_to_srgb(lightness, nums[1], nums[2])
        return rgb, nums[3] if len(nums) > 3 else 1.0, in_gamut
    raise ValueError(f"unsupported color: {value}")


def luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = (_srgb_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: str, bg: str) -> tuple[float, list[str]]:
    notes = []
    bg_rgb, bg_alpha, bg_gamut = parse(bg)
    fg_rgb, fg_alpha, fg_gamut = parse(fg)
    if bg_alpha < 1:
        notes.append("background is translucent; result assumes it is opaque")
    if fg_alpha < 1:
        fg_rgb = tuple(f * fg_alpha + b * (1 - fg_alpha) for f, b in zip(fg_rgb, bg_rgb))
    if not (fg_gamut and bg_gamut):
        notes.append("outside sRGB; browsers map it, so check the rendered color")
    la, lb = luminance(fg_rgb), luminance(bg_rgb)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05), notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WCAG contrast for color pairs (hex, rgb, hsl, oklch).")
    parser.add_argument("colors", nargs="+", help="FOREGROUND BACKGROUND pairs")
    parser.add_argument("--min", type=float, default=4.5, help="minimum ratio for the exit status (default 4.5)")
    args = parser.parse_args(argv)
    if len(args.colors) % 2:
        parser.error("give colors in FOREGROUND BACKGROUND pairs")
    failed = False
    for fg, bg in zip(args.colors[::2], args.colors[1::2]):
        try:
            value, notes = ratio(fg, bg)
        except ValueError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        verdicts = [
            f"text {'pass' if value >= 4.5 else 'FAIL'} (4.5)",
            f"large/UI {'pass' if value >= 3 else 'FAIL'} (3)",
            f"AAA {'pass' if value >= 7 else 'no'} (7)",
        ]
        failed = failed or value < args.min
        extra = f"  [{'; '.join(notes)}]" if notes else ""
        print(f"{value:5.2f}:1  {fg}  on  {bg}  — {', '.join(verdicts)}{extra}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
