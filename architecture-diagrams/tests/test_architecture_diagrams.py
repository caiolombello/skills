"""Regression tests for the architecture-diagrams skill tooling."""

from __future__ import annotations

import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET
import zlib


SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import autolayout  # noqa: E402
import c4  # noqa: E402
import k8simports  # noqa: E402
import preflight  # noqa: E402
import render_excalidraw  # noqa: E402
import repair_png  # noqa: E402
import tfstate  # noqa: E402


class RuntimeTests(unittest.TestCase):
    def test_vendored_runtime_integrity(self):
        ok, detail = preflight.runtime_integrity()
        self.assertTrue(ok, detail)

    def test_runtime_rejects_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle.js"
            manifest = root / "manifest.json"
            bundle.write_text("tampered", encoding="utf-8")
            manifest.write_text(
                json.dumps({"bundle_sha256": "0" * 64}), encoding="utf-8"
            )
            with (
                mock.patch.object(render_excalidraw, "RENDERER_BUNDLE", bundle),
                mock.patch.object(render_excalidraw, "RUNTIME_MANIFEST", manifest),
            ):
                with self.assertRaisesRegex(RuntimeError, "integrity check failed"):
                    render_excalidraw.load_runtime()

    def test_renderer_template_has_no_network_runtime(self):
        template = (SKILL_ROOT / "assets" / "excalidraw-renderer.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("connect-src 'none'", template)
        self.assertNotIn("cdn.jsdelivr", template)
        self.assertNotIn("https://", template)

    def test_svg_and_png_destinations_must_differ(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "scene.excalidraw"
            output = root / "same-output"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must differ"):
                render_excalidraw.ensure_writable(
                    source, (output, output), force=False
                )

    def test_browser_checks_remain_active_after_scene_render(self):
        with self.assertRaisesRegex(RuntimeError, "scene render"):
            render_excalidraw.ensure_browser_clean(
                [], ["https://example.invalid/late-request"], "scene render"
            )


class DrawioIdTests(unittest.TestCase):
    def test_edge_id_does_not_collide_with_user_node(self):
        graph = {
            "nodes": [{"id": "e0"}, {"id": "target"}],
            "edges": [{"source": "e0", "target": "target"}],
        }
        xml = autolayout.to_drawio(
            graph,
            height=2.0,
            pos={"e0": (1.0, 1.0), "target": (3.0, 1.0)},
            edge_pts={},
        )
        cells = ET.fromstring(xml).findall(".//mxCell")
        ids = [cell.get("id") for cell in cells if cell.get("id")]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("e0_", ids)

    def test_graph_contract_rejects_reserved_and_dangling_ids(self):
        with self.assertRaisesRegex(ValueError, "reserved"):
            autolayout.validate_graph({"nodes": [{"id": "0"}], "edges": []})
        with self.assertRaisesRegex(ValueError, "is not a node id"):
            autolayout.validate_graph(
                {
                    "nodes": [{"id": "a"}],
                    "edges": [{"source": "a", "target": "missing"}],
                }
            )

    def test_c4_slug_collisions_get_distinct_page_ids(self):
        ids = c4.unique_page_ids(["Foo Bar", "Foo-Bar", "Other"])
        self.assertEqual(ids["Foo Bar"], "foo-bar")
        self.assertEqual(ids["Foo-Bar"], "foo-bar-2")
        self.assertEqual(len(set(ids.values())), 3)

    def test_validator_rejects_duplicate_page_ids(self):
        page = """
  <diagram id="same" name="{name}">
    <mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>
  </diagram>"""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "duplicate-pages.drawio"
            source.write_text(
                "<mxfile>" + page.format(name="One") + page.format(name="Two") + "</mxfile>",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate.py"), str(source)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate page id", result.stdout)


class TerraformTests(unittest.TestCase):
    def test_saved_plan_uses_configuration_references(self):
        actual = {"terraform_data.consumer", "terraform_data.seed"}
        configuration = {
            "root_module": {
                "resources": [
                    {
                        "address": "terraform_data.consumer",
                        "mode": "managed",
                        "expressions": {
                            "input": {
                                "references": [
                                    "terraform_data.seed.output",
                                    "terraform_data.seed",
                                ]
                            }
                        },
                    },
                    {
                        "address": "terraform_data.seed",
                        "mode": "managed",
                        "expressions": {"input": {"constant_value": "x"}},
                    },
                ]
            }
        }
        self.assertEqual(
            tfstate.configuration_edges(configuration, actual),
            {("terraform_data.consumer", "terraform_data.seed")},
        )

    def test_module_instances_do_not_cross_wire(self):
        actual = {
            "module.child[0].terraform_data.consumer",
            "module.child[0].terraform_data.seed",
            "module.child[1].terraform_data.consumer",
            "module.child[1].terraform_data.seed",
        }
        configuration = {
            "root_module": {
                "module_calls": {
                    "child": {
                        "module": {
                            "resources": [
                                {
                                    "address": "terraform_data.consumer",
                                    "mode": "managed",
                                    "expressions": {
                                        "input": {
                                            "references": ["terraform_data.seed"]
                                        }
                                    },
                                },
                                {
                                    "address": "terraform_data.seed",
                                    "mode": "managed",
                                    "expressions": {},
                                },
                            ]
                        }
                    }
                }
            }
        }
        self.assertEqual(
            tfstate.configuration_edges(configuration, actual),
            {
                (
                    "module.child[0].terraform_data.consumer",
                    "module.child[0].terraform_data.seed",
                ),
                (
                    "module.child[1].terraform_data.consumer",
                    "module.child[1].terraform_data.seed",
                ),
            },
        )

    def test_recorded_state_depends_on_is_optional_and_expandable(self):
        resources = [
            (
                "module.child[0].terraform_data.consumer",
                "terraform_data",
                "consumer",
                None,
                "module.child[0]",
                ["module.child.terraform_data.seed"],
            ),
            (
                "module.child[0].terraform_data.seed",
                "terraform_data",
                "seed",
                None,
                "module.child[0]",
                [],
            ),
        ]
        self.assertEqual(
            tfstate.recorded_dependency_edges(resources),
            {
                (
                    "module.child[0].terraform_data.consumer",
                    "module.child[0].terraform_data.seed",
                )
            },
        )


class KubernetesTests(unittest.TestCase):
    def test_implicit_namespace_is_default_but_cluster_scope_is_empty(self):
        deployment = {"kind": "Deployment", "metadata": {"name": "api"}}
        namespace = {"kind": "Namespace", "metadata": {"name": "default"}}
        self.assertEqual(k8simports.object_namespace(deployment), "default")
        self.assertEqual(k8simports.object_namespace(namespace), "")

    def test_implicit_and_explicit_default_namespace_link(self):
        manifest = {
            "kind": "List",
            "items": [
                {
                    "kind": "Service",
                    "metadata": {"name": "api", "namespace": "default"},
                    "spec": {"selector": {"app": "api"}},
                },
                {
                    "kind": "Deployment",
                    "metadata": {"name": "api"},
                    "spec": {
                        "template": {
                            "metadata": {"labels": {"app": "api"}},
                            "spec": {"containers": [{"name": "api"}]},
                        }
                    },
                },
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "objects.json", root / "graph.json"
            source.write_text(json.dumps(manifest), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "k8simports.py"),
                    str(source),
                    "--no-icons",
                    "-o",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            graph = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(
            graph["edges"],
            [
                {
                    "source": "default/Service/api",
                    "target": "default/Deployment/api",
                }
            ],
        )


class PngRepairTests(unittest.TestCase):
    @staticmethod
    def chunk(kind: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)

    @classmethod
    def valid_png(cls) -> bytes:
        ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
        return (
            repair_png.SIGNATURE
            + cls.chunk(b"IHDR", ihdr)
            + cls.chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00\x00"))
            + repair_png.IEND
        )

    def test_exact_truncated_iend_is_repaired(self):
        valid = self.valid_png()
        truncated = valid[:-8]
        self.assertEqual(repair_png.inspect_png(truncated), "truncated-iend")
        self.assertEqual(repair_png.repaired_bytes(truncated), valid)

    def test_valid_png_with_trailing_data_is_not_modified(self):
        data = self.valid_png() + b"trailing metadata"
        self.assertEqual(repair_png.inspect_png(data), "valid")
        self.assertIsNone(repair_png.repaired_bytes(data))

    def test_non_png_and_bad_crc_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "signature"):
            repair_png.repaired_bytes(b"not a png")
        damaged = bytearray(self.valid_png())
        damaged[20] ^= 0x01
        with self.assertRaisesRegex(ValueError, "invalid CRC"):
            repair_png.repaired_bytes(bytes(damaged))

    def test_output_cannot_alias_input_without_in_place(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "truncated.png"
            source.write_bytes(self.valid_png()[:-8])
            before = source.read_bytes()
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "repair_png.py"),
                    str(source),
                    "--output",
                    str(source.parent / "." / source.name),
                    "--force",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("use --in-place", result.stderr)
            self.assertEqual(source.read_bytes(), before)

    def test_hard_link_output_cannot_replace_input_without_in_place(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "truncated.png"
            alias = Path(directory) / "hard-link.png"
            source.write_bytes(self.valid_png()[:-8])
            alias.hardlink_to(source)
            before = source.read_bytes()
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "repair_png.py"),
                    str(source),
                    "--output",
                    str(alias),
                    "--force",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("use --in-place", result.stderr)
            self.assertEqual(source.read_bytes(), before)


class LicenseTests(unittest.TestCase):
    def test_vendored_assets_have_full_license_notices(self):
        apache = SKILL_ROOT / "references" / "licenses" / "Apache-2.0.txt"
        notices = (
            SKILL_ROOT
            / "references"
            / "licenses"
            / "excalidraw-renderer-third-party-notices.txt"
        )
        self.assertIn("Apache License", apache.read_text(encoding="utf-8"))
        text = notices.read_text(encoding="utf-8")
        self.assertIn("@excalidraw/excalidraw@0.18.1", text)
        self.assertIn("browser-fs-access@0.29.1", text)


if __name__ == "__main__":
    unittest.main()
