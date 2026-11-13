"""Focused coverage for count/for_each dependency expansion in tfstate.py."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import tfstate  # noqa: E402


def configuration_for(*references: str) -> dict:
    return {
        "root_module": {
            "resources": [
                {
                    "address": "terraform_data.consumer",
                    "mode": "managed",
                    "expressions": {"input": {"references": list(references)}},
                },
                {
                    "address": "terraform_data.seed",
                    "mode": "managed",
                    "expressions": {},
                },
            ]
        }
    }


class TerraformResourceInstanceTests(unittest.TestCase):
    def test_count_index_expression_omits_unresolved_instance_mapping(self):
        actual = {
            "terraform_data.consumer[0]",
            "terraform_data.consumer[1]",
            "terraform_data.seed[0]",
            "terraform_data.seed[1]",
        }
        warnings = set()
        edges = tfstate.configuration_edges(
            configuration_for("terraform_data.seed", "count.index"), actual, warnings
        )
        self.assertEqual(edges, set())
        self.assertIn("does not preserve an instance mapping", next(iter(warnings)))

    def test_each_key_expression_omits_unresolved_instance_mapping(self):
        actual = {
            'terraform_data.consumer["blue.us-east-1"]',
            'terraform_data.consumer["green.eu-west-1"]',
            'terraform_data.seed["blue.us-east-1"]',
            'terraform_data.seed["green.eu-west-1"]',
        }
        warnings = set()
        edges = tfstate.configuration_edges(
            configuration_for("terraform_data.seed", "each.key"), actual, warnings
        )
        self.assertEqual(edges, set())
        self.assertIn("does not preserve an instance mapping", next(iter(warnings)))

    def test_each_value_expression_is_also_treated_as_ambiguous(self):
        actual = {
            'terraform_data.consumer["first"]',
            'terraform_data.consumer["second"]',
            'terraform_data.seed["blue"]',
            'terraform_data.seed["green"]',
        }
        warnings = set()
        edges = tfstate.configuration_edges(
            configuration_for("terraform_data.seed", "each.value"), actual, warnings
        )
        self.assertEqual(edges, set())
        self.assertIn("dynamic or unresolved references", next(iter(warnings)))

    def test_static_multi_instance_reference_is_omitted_as_ambiguous(self):
        actual = {
            "terraform_data.consumer[0]",
            "terraform_data.consumer[1]",
            "terraform_data.seed[0]",
            "terraform_data.seed[1]",
        }
        warnings = set()
        self.assertEqual(
            tfstate.configuration_edges(configuration_for("terraform_data.seed"), actual, warnings),
            set(),
        )
        self.assertIn("does not preserve whether one or all instances", next(iter(warnings)))

    def test_static_multi_instance_result_does_not_depend_on_warning_collector(self):
        actual = {
            "terraform_data.consumer[0]",
            "terraform_data.consumer[1]",
            "terraform_data.seed[0]",
            "terraform_data.seed[1]",
        }
        self.assertEqual(
            tfstate.configuration_edges(configuration_for("terraform_data.seed"), actual),
            set(),
        )

    def test_literal_target_index_connects_only_that_target(self):
        actual = {
            "terraform_data.consumer[0]",
            "terraform_data.consumer[1]",
            "terraform_data.seed[0]",
            "terraform_data.seed[1]",
        }
        self.assertEqual(
            tfstate.configuration_edges(configuration_for("terraform_data.seed[0]"), actual),
            {
                ("terraform_data.consumer[0]", "terraform_data.seed[0]"),
                ("terraform_data.consumer[1]", "terraform_data.seed[0]"),
            },
        )

    def test_static_state_depends_on_omits_multi_instance_relation(self):
        resources = [
            ("terraform_data.consumer[0]", "terraform_data", "consumer", 0, "", ["terraform_data.seed"]),
            ("terraform_data.consumer[1]", "terraform_data", "consumer", 1, "", ["terraform_data.seed"]),
            ("terraform_data.seed[0]", "terraform_data", "seed", 0, "", []),
            ("terraform_data.seed[1]", "terraform_data", "seed", 1, "", []),
        ]
        warnings = set()
        self.assertEqual(tfstate.recorded_dependency_edges(resources, warnings), set())
        self.assertIn("ambiguous recorded state dependency omitted", next(iter(warnings)))

    def test_exact_state_instance_dependencies_do_not_cross_wire(self):
        resources = [
            ("terraform_data.consumer[0]", "terraform_data", "consumer", 0, "", ["terraform_data.seed[0]"]),
            ("terraform_data.consumer[1]", "terraform_data", "consumer", 1, "", ["terraform_data.seed[1]"]),
            ("terraform_data.seed[0]", "terraform_data", "seed", 0, "", []),
            ("terraform_data.seed[1]", "terraform_data", "seed", 1, "", []),
        ]
        self.assertEqual(
            tfstate.recorded_dependency_edges(resources),
            {
                ("terraform_data.consumer[0]", "terraform_data.seed[0]"),
                ("terraform_data.consumer[1]", "terraform_data.seed[1]"),
            },
        )

    def test_instance_mapping_signal_is_scoped_to_its_expression(self):
        configuration = configuration_for("terraform_data.seed")
        configuration["root_module"]["resources"][0]["expressions"]["other"] = {
            "references": ["count.index"]
        }
        actual = {
            "terraform_data.consumer[0]",
            "terraform_data.consumer[1]",
            "terraform_data.seed[0]",
            "terraform_data.seed[1]",
        }
        warnings = set()
        self.assertEqual(
            tfstate.configuration_edges(configuration, actual, warnings),
            set(),
        )
        self.assertIn("static resource reference", next(iter(warnings)))

    def test_quoted_and_escaped_index_keys_are_parsed_without_regex_confusion(self):
        address = 'module.child["a]b"].terraform_data.x["a]b"]'
        escaped = 'terraform_data.x["a\\"b]c"]'
        self.assertEqual(tfstate.static_address(address), "module.child.terraform_data.x")
        self.assertEqual(tfstate.module_prefix(address), 'module.child["a]b"]')
        self.assertEqual(tfstate.resource_instance_key(address), '"a]b"')
        self.assertEqual(tfstate.static_address(escaped), "terraform_data.x")
        self.assertEqual(tfstate.resource_instance_key(escaped), '"a\\"b]c"')

    def test_ambiguous_instances_cli_warns(self):
        actual = {
            "terraform_data.consumer[0]",
            "terraform_data.consumer[1]",
            "terraform_data.seed[0]",
            "terraform_data.seed[1]",
        }

        plan = {
            "planned_values": {
                "root_module": {
                    "resources": [
                        {"address": address, "mode": "managed", "type": "terraform_data",
                         "name": address.split(".")[1].split("[")[0]}
                        for address in sorted(actual)
                    ]
                }
            },
            "configuration": configuration_for("terraform_data.seed", "count.index"),
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "plan.json"
            source.write_text(json.dumps(plan), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "tfstate.py"),
                    str(source),
                    "--no-icons",
                    "--no-reduce",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("warning: ambiguous Terraform dependency omitted", result.stderr)
        self.assertIn("dependency source: saved-plan configuration references", result.stderr)
        self.assertNotIn("inventory only", result.stderr)
        self.assertEqual(json.loads(result.stdout)["edges"], [])

    def test_resolved_plan_does_not_claim_inventory_only(self):
        actual = {
            "terraform_data.consumer[0]",
            "terraform_data.seed[0]",
        }
        plan = {
            "planned_values": {
                "root_module": {
                    "resources": [
                        {
                            "address": address,
                            "mode": "managed",
                            "type": "terraform_data",
                            "name": address.split(".")[1].split("[")[0],
                        }
                        for address in sorted(actual)
                    ]
                }
            },
            "configuration": configuration_for("terraform_data.seed"),
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "plan.json"
            source.write_text(json.dumps(plan), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "tfstate.py"),
                    str(source),
                    "--no-icons",
                    "--no-reduce",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("dependency source: saved-plan configuration references", result.stderr)
        self.assertNotIn("inventory only", result.stderr)


if __name__ == "__main__":
    unittest.main()
