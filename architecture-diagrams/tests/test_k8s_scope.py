"""Regression tests for Kubernetes namespace/scope classification."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import k8simports  # noqa: E402


class KubernetesScopeTests(unittest.TestCase):
    def test_common_cluster_scoped_kinds_have_no_namespace(self):
        for kind in {
            "CertificateSigningRequest",
            "CSIDriver",
            "CSINode",
            "FlowSchema",
            "GatewayClass",
            "IngressClass",
            "RuntimeClass",
            "ValidatingAdmissionPolicy",
            "ValidatingAdmissionPolicyBinding",
            "VolumeAttachment",
        }:
            with self.subTest(kind=kind):
                self.assertEqual(
                    k8simports.object_namespace({"kind": kind, "metadata": {"name": "x"}}),
                    "",
                )

    def test_common_core_namespaced_kinds_default_correctly(self):
        for kind in ("LimitRange", "ResourceQuota", "ReplicationController"):
            with self.subTest(kind=kind):
                self.assertEqual(
                    k8simports.object_namespace(
                        {"apiVersion": "v1", "kind": kind, "metadata": {"name": "x"}}
                    ),
                    "default",
                )

    def test_unknown_custom_resource_without_namespace_keeps_scope_unknown(self):
        obj = {"apiVersion": "example.io/v1", "kind": "Widget", "metadata": {"name": "blue"}}
        self.assertIsNone(k8simports.object_namespace(obj))

    def test_unknown_custom_resource_preserves_explicit_namespace(self):
        obj = {
            "apiVersion": "example.io/v1",
            "kind": "Widget",
            "metadata": {"name": "blue", "namespace": "platform"},
        }
        self.assertEqual(k8simports.object_namespace(obj), "platform")

    def test_unknown_custom_resource_node_declares_scope_uncertainty(self):
        manifest = {
            "apiVersion": "example.io/v1",
            "kind": "Widget",
            "metadata": {"name": "blue"},
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "widget.json"
            output = Path(directory) / "graph.json"
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
            graph["nodes"],
            [{
                "id": "scope-unknown/example.io/Widget/blue",
                "label": "blue\nWidget\nAPI group: example.io\nscope unknown",
            }],
        )

    def test_custom_kind_reusing_builtin_name_does_not_infer_builtin_scope(self):
        for kind in {"Deployment", "Namespace"}:
            with self.subTest(kind=kind):
                obj = {
                    "apiVersion": "example.io/v1",
                    "kind": kind,
                    "metadata": {"name": "blue"},
                }
                self.assertIsNone(k8simports.object_namespace(obj))

    def test_same_name_and_kind_in_distinct_api_groups_remain_distinct(self):
        manifest = {
            "kind": "List",
            "items": [
                {
                    "apiVersion": "example.io/v1",
                    "kind": "Widget",
                    "metadata": {"name": "blue", "namespace": "platform"},
                },
                {
                    "apiVersion": "other.io/v1",
                    "kind": "Widget",
                    "metadata": {"name": "blue", "namespace": "platform"},
                },
            ],
        }
        graph = self.run_import(manifest)
        self.assertEqual(
            {node["id"] for node in graph["nodes"]},
            {"platform/example.io/Widget/blue", "platform/other.io/Widget/blue"},
        )

    def test_multigroup_builtin_ids_are_unique_and_inference_is_deterministic(self):
        manifest = {
            "kind": "List",
            "items": [
                {
                    "apiVersion": "v1",
                    "kind": "Event",
                    "metadata": {"name": "same", "namespace": "default"},
                },
                {
                    "apiVersion": "events.k8s.io/v1",
                    "kind": "Event",
                    "metadata": {"name": "same", "namespace": "default"},
                },
            ],
        }
        graph = self.run_import(manifest)
        self.assertEqual(
            {node["id"] for node in graph["nodes"]},
            {"default/Event/same", "default/events.k8s.io/Event/same"},
        )
        self.assertEqual(
            k8simports.object_group({"kind": "Event", "metadata": {"name": "x"}}),
            "",
        )

    def test_service_selector_ignores_custom_deployment_with_same_name(self):
        manifest = {
            "kind": "List",
            "items": [
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {"name": "api", "namespace": "default"},
                    "spec": {"selector": {"app": "api"}},
                },
                {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "metadata": {"name": "api", "namespace": "default"},
                    "spec": {"template": {"metadata": {"labels": {"app": "api"}}}},
                },
                {
                    "apiVersion": "example.io/v1",
                    "kind": "Deployment",
                    "metadata": {"name": "api", "namespace": "default"},
                    "spec": {"template": {"metadata": {"labels": {"app": "api"}}}},
                },
            ],
        }
        graph = self.run_import(manifest)
        self.assertEqual(
            graph["edges"],
            [{"source": "default/Service/api", "target": "default/Deployment/api"}],
        )

    def test_custom_kind_reusing_builtin_name_does_not_get_builtin_icon(self):
        manifest = {
            "apiVersion": "example.io/v1",
            "kind": "Deployment",
            "metadata": {"name": "custom", "namespace": "platform"},
        }
        graph = self.run_import(manifest, no_icons=False)
        self.assertNotIn("style", graph["nodes"][0])
        self.assertIn("API group: example.io", graph["nodes"][0]["label"])

    def test_unknown_core_kind_preserves_known_core_group(self):
        manifest = {
            "apiVersion": "v1",
            "kind": "FutureCoreKind",
            "metadata": {"name": "future"},
        }
        graph = self.run_import(manifest)
        self.assertEqual(
            graph["nodes"][0]["id"],
            "scope-unknown/core/FutureCoreKind/future",
        )
        self.assertIn("API group: core", graph["nodes"][0]["label"])

    def test_legacy_ingress_backend_links_to_core_service(self):
        manifest = {
            "kind": "List",
            "items": [
                {
                    "apiVersion": "extensions/v1beta1",
                    "kind": "Ingress",
                    "metadata": {"name": "legacy", "namespace": "default"},
                    "spec": {
                        "rules": [
                            {
                                "http": {
                                    "paths": [
                                        {"backend": {"serviceName": "api", "servicePort": 80}}
                                    ]
                                }
                            }
                        ]
                    },
                },
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {"name": "api", "namespace": "default"},
                    "spec": {},
                },
            ],
        }
        graph = self.run_import(manifest)
        self.assertEqual(
            graph["edges"],
            [
                {
                    "source": "default/extensions/Ingress/legacy",
                    "target": "default/Service/api",
                }
            ],
        )

    @staticmethod
    def run_import(manifest, no_icons=True):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "objects.json"
            output = Path(directory) / "graph.json"
            source.write_text(json.dumps(manifest), encoding="utf-8")
            command = [
                sys.executable,
                str(SCRIPTS / "k8simports.py"),
                str(source),
                "-o",
                str(output),
            ]
            if no_icons:
                command.insert(-2, "--no-icons")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode:
                raise AssertionError(result.stderr)
            return json.loads(output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
