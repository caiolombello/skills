"""Optional real-browser smoke test for the pinned Excalidraw renderer.

Set ARCHITECTURE_DIAGRAMS_E2E_BROWSER to a Chromium-compatible executable and
run this test through a Python environment containing playwright==1.62.0.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import render_excalidraw  # noqa: E402


BROWSER = os.environ.get("ARCHITECTURE_DIAGRAMS_E2E_BROWSER")
CAN_RUN = bool(
    BROWSER
    and Path(BROWSER).is_file()
    and importlib.util.find_spec("playwright") is not None
)


@unittest.skipUnless(
    CAN_RUN,
    "set ARCHITECTURE_DIAGRAMS_E2E_BROWSER and install playwright==1.62.0",
)
class ExcalidrawRendererE2ETests(unittest.TestCase):
    def test_local_offline_svg_and_png_render(self):
        scene = {
            "type": "excalidraw",
            "version": 2,
            "source": "architecture-diagrams-e2e",
            "elements": [
                {
                    "id": "system-a",
                    "type": "rectangle",
                    "x": 0,
                    "y": 0,
                    "width": 240,
                    "height": 100,
                    "angle": 0,
                    "strokeColor": "#1e1e1e",
                    "backgroundColor": "#dbeafe",
                    "fillStyle": "solid",
                    "strokeWidth": 2,
                    "strokeStyle": "solid",
                    "roughness": 0,
                    "opacity": 100,
                    "groupIds": [],
                    "frameId": None,
                    "index": "a0",
                    "roundness": {"type": 3},
                    "seed": 1,
                    "version": 1,
                    "versionNonce": 1,
                    "isDeleted": False,
                    "boundElements": [],
                    "updated": 1,
                    "link": None,
                    "locked": False,
                }
            ],
            "appState": {"viewBackgroundColor": "#ffffff"},
            "files": {},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            svg = root / "smoke.svg"
            png = root / "smoke.png"
            render_excalidraw.render(
                scene,
                svg,
                png,
                scale=1.0,
                padding=16,
                transparent=False,
                timeout_seconds=45.0,
                browser_executable=BROWSER,
            )
            self.assertIn("<svg", svg.read_text(encoding="utf-8"))
            self.assertGreater(png.stat().st_size, 100)
            self.assertEqual(png.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
