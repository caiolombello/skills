"""Markdown-to-ADF conversion used before sending Jira bodies through acli."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "atlassian-acli/scripts"))
import md2adf  # noqa: E402


def _types(nodes):
    return [node["type"] for node in nodes]


def _marks(node):
    return [mark["type"] for mark in node.get("marks", [])]


class MarkdownToAdfTests(unittest.TestCase):
    def test_card_markdown_becomes_structured_adf_not_literal_text(self):
        doc = md2adf.convert(
            "## Objetivo\n\n"
            "Atualizar **todos os repositórios** na branch `main`.\n\n"
            "**Repositórios ativos:**\n"
            "- AngularWorkingOps\n"
            "- BackendServelessWorkingOps (Lambdas)\n"
        )

        self.assertEqual(doc["type"], "doc")
        self.assertEqual(doc["version"], 1)
        self.assertEqual(_types(doc["content"]), ["heading", "paragraph", "paragraph", "bulletList"])
        self.assertEqual(doc["content"][0]["attrs"], {"level": 2})
        paragraph = doc["content"][1]["content"]
        self.assertEqual(_marks(paragraph[1]), ["strong"])
        self.assertEqual(paragraph[3]["text"], "main")
        self.assertEqual(_marks(paragraph[3]), ["code"])
        self.assertEqual(len(doc["content"][3]["content"]), 2)
        serialized = str(doc)
        self.assertNotIn("##", serialized)
        self.assertNotIn("**", serialized)

    def test_nested_and_ordered_lists(self):
        doc = md2adf.convert("1. um\n   - filho\n2. dois\n")
        ordered = doc["content"][0]
        self.assertEqual(ordered["type"], "orderedList")
        self.assertEqual(ordered["attrs"], {"order": 1})
        self.assertEqual(_types(ordered["content"][0]["content"]), ["paragraph", "bulletList"])
        self.assertEqual(len(ordered["content"]), 2)

    def test_code_block_keeps_markdown_literal(self):
        doc = md2adf.convert("```bash\necho '**x**'\n```\n")
        block = doc["content"][0]
        self.assertEqual(block["type"], "codeBlock")
        self.assertEqual(block["attrs"], {"language": "bash"})
        self.assertEqual(block["content"][0]["text"], "echo '**x**'")

    def test_table_link_and_snake_case(self):
        doc = md2adf.convert(
            "| Repo | Link |\n|---|---|\n| api_tools_x | [docs](https://example.com/a_(b)) |\n"
        )
        table = doc["content"][0]
        self.assertEqual(table["type"], "table")
        header, row = table["content"]
        self.assertEqual(_types(header["content"]), ["tableHeader", "tableHeader"])
        first_cell = row["content"][0]["content"][0]["content"][0]
        self.assertEqual(first_cell, {"type": "text", "text": "api_tools_x"})
        link = row["content"][1]["content"][0]["content"][0]
        self.assertEqual(link["marks"], [{"type": "link", "attrs": {"href": "https://example.com/a_(b)"}}])

    def test_code_mark_is_not_combined_with_strong(self):
        doc = md2adf.convert("**`x` y**")
        code, text = doc["content"][0]["content"]
        self.assertEqual(_marks(code), ["code"])
        self.assertEqual(_marks(text), ["strong"])

    def test_empty_input_is_rejected(self):
        self.assertEqual(md2adf.convert("\n\n")["content"], [])


if __name__ == "__main__":
    unittest.main()
