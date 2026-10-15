"""Synthetic fixtures only. No publication source code or fixture code is executed."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check_publication", HERE / "check_publication.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "book"
        self.root.mkdir()
        self.contract = {"schema": "publication-integrity-contract/v1", "repository_prefix": "books/claude-app", "required": [], "manifests": []}

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def run_check(self):
        tree = checker.SafeTree(str(self.root))
        try:
            return checker.Checker(tree, self.contract).run()
        finally:
            tree.close()

    def codes(self, result):
        return {item["code"] for item in result["issues"]}

    def test_contract_has_expected_inventory(self):
        contract = checker.validate_contract(json.loads((HERE / "contract.json").read_text()))
        groups = {x["name"]: x["paths"] for x in contract["required"]}
        for group, count in (("six_templates", 6), ("sixteen_core_chapters", 16), ("three_supplement_chapters", 3), ("seven_mechanism_skills", 7)):
            self.assertEqual(len(groups[group]), count)
        self.assertEqual(len(contract["manifests"]), 4)
        self.assertIn("04-Extracted-Core-Code-And-Scripts/core-code-lab/manifest.json", contract["manifests"])

    def test_registered_core_manifest_catches_new_overlay_drift(self):
        contract = checker.validate_contract(json.loads((HERE / "contract.json").read_text()))
        manifest_path = "04-Extracted-Core-Code-And-Scripts/core-code-lab/manifest.json"
        self.assertIn(manifest_path, contract["manifests"])
        self.contract["manifests"] = [manifest_path]
        folder = str(Path(manifest_path).parent)
        source = self.write(folder + "/color-tools/resolution_overlay.py", "# synthetic source\n")
        raw = source.read_bytes()
        self.write(manifest_path, json.dumps({"format_version": 1, "files": [{
            "path": "color-tools/resolution_overlay.py", "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(), "source": "original-integration", "copy": "new"
        }]}))
        clean = self.run_check()
        self.assertEqual(clean["status"], "passed", clean)
        self.assertEqual(clean["manifests"][0]["matched"], 1)
        source.write_text("# synthetic drift!\n", encoding="utf-8")
        dirty = self.run_check()
        self.assertEqual(dirty["status"], "failed", dirty)
        self.assertIn("manifest_hash_drift", self.codes(dirty))

    def test_duplicate_headings_and_collision_suffix(self):
        self.write("README.md", "# Hello\n# Hello\n# Hello-1\n# Hello\n[x](#hello) [x](#hello-1) [x](#hello-1-1) [x](#hello-2)\n")
        result = self.run_check()
        self.assertEqual(result["status"], "passed", result)
        self.assertEqual(result["summary"]["heading_fragments_checked"], 4)

    def test_escaped_parentheses_and_angle_space_path(self):
        self.write("a(b).md", "# Target\n")
        self.write("a b.md", "# Target\n")
        self.write("README.md", r"[a](a\(b\).md#target) [b](<a b.md#target>)" + "\n")
        self.assertEqual(self.run_check()["status"], "passed")

    def test_percent_encoded_paths_fragments_and_literal_hash(self):
        self.write("space 中文#.md", "# 中文 测试\n")
        self.write("README.md", "[x](space%20%E4%B8%AD%E6%96%87%23.md#%E4%B8%AD%E6%96%87-%E6%B5%8B%E8%AF%95)\n")
        self.assertEqual(self.run_check()["status"], "passed")

    def test_external_url_fragments_not_checked_and_queries_ignored(self):
        self.write("target.md", "# Good\n")
        self.write("README.md", "[external](https://example.invalid/a#missing) [local](target.md?raw=1#good)\n")
        result = self.run_check()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["summary"]["external_links_not_checked"], 1)
        self.assertEqual(result["summary"]["local_queries_ignored"], 1)

    def test_missing_file_and_heading_are_errors(self):
        self.write("README.md", "# Present\n[x](missing.md) [y](#absent)\n")
        self.assertEqual(self.codes(self.run_check()), {"missing_path", "missing_heading"})

    def test_fragment_matching_is_case_sensitive(self):
        self.write("README.md", "# Title\n[x](#Title)\n")
        self.assertIn("missing_heading", self.codes(self.run_check()))

    def test_outside_root_link_and_percent_traversal(self):
        outside = Path(self.tmp.name) / "outside.md"
        outside.write_text("# Outside\n")
        self.write("README.md", "[a](../outside.md) [b](%2e%2e/outside.md) [c](/README.md)\n")
        result = self.run_check()
        self.assertEqual([x["code"] for x in result["issues"]], ["outside_root"] * 3)
        self.assertEqual(result["summary"]["markdown_files_read"], 1)

    def test_repository_prefix_maps_to_book_root(self):
        self.write("docs/a.md", "# Hello\n")
        self.write("README.md", "[x](/books/claude-app/docs/a.md#hello)\n")
        self.assertEqual(self.run_check()["status"], "passed")

    def test_symlink_file_and_parent_are_not_read(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (outside / "secret.md").write_text("# Should never be read\n")
        (self.root / "linked.md").symlink_to(outside / "secret.md")
        (self.root / "linked-dir").symlink_to(outside, target_is_directory=True)
        self.write("README.md", "[a](linked.md) [b](linked-dir/secret.md)\n")
        result = self.run_check()
        self.assertEqual(result["summary"]["markdown_files_read"], 1)
        self.assertEqual(self.codes(result), {"symlink_rejected"})
        self.assertEqual(len(result["issues"]), 4)

    def test_symlink_root_rejected(self):
        alias = Path(self.tmp.name) / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(checker.CheckError) as error:
            checker.SafeTree(str(alias))
        self.assertEqual(error.exception.code, "root_unreadable")

    def test_manifest_array_hash_size_missing_and_drift(self):
        self.write("pack/a.txt", "original")
        digest = hashlib.sha256(b"original").hexdigest()
        manifest = {"files": [{"path": "a.txt", "bytes": 8, "sha256": digest}]}
        self.write("pack/manifest.json", json.dumps(manifest))
        self.contract["manifests"] = ["pack/manifest.json"]
        self.assertEqual(self.run_check()["status"], "passed")
        self.write("pack/a.txt", "changed")
        self.assertIn("manifest_hash_drift", self.codes(self.run_check()))
        self.write("pack/a.txt", "original")
        manifest["files"][0]["bytes"] = 7
        self.write("pack/manifest.json", json.dumps(manifest))
        self.assertIn("manifest_size_drift", self.codes(self.run_check()))
        (self.root / "pack/a.txt").unlink()
        self.assertIn("missing_path", self.codes(self.run_check()))

    def test_manifest_mapping_form(self):
        self.write("lesson/index.html", "<h1>Synthetic</h1>")
        digest = hashlib.sha256((self.root / "lesson/index.html").read_bytes()).hexdigest()
        self.write("lesson/validation.json", json.dumps({"files": {"index.html": digest}}))
        self.contract["manifests"] = ["lesson/validation.json"]
        result = self.run_check()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["manifests"][0]["matched"], 1)

    def test_manifest_cannot_escape_root_or_read_symlink(self):
        self.write("pack/manifest.json", json.dumps({"files": {"../../outside.txt": "0" * 64}}))
        self.contract["manifests"] = ["pack/manifest.json"]
        self.assertIn("outside_root", self.codes(self.run_check()))
        (self.root / "pack/link.txt").symlink_to(Path(self.tmp.name) / "outside.txt")
        self.write("pack/manifest.json", json.dumps({"files": {"link.txt": "0" * 64}}))
        self.assertIn("symlink_rejected", self.codes(self.run_check()))

    def test_manifest_duplicate_and_invalid_shape(self):
        self.write("a.txt", "a")
        digest = hashlib.sha256(b"a").hexdigest()
        self.write("m.json", json.dumps({"files": [{"path": "a.txt", "sha256": digest}, {"path": "./a.txt", "sha256": digest}, {}]}))
        self.contract["manifests"] = ["m.json"]
        self.assertEqual(self.codes(self.run_check()), {"manifest_duplicate", "manifest_schema"})

    def test_required_missing_and_wrong_kind(self):
        self.write("directory", "file")
        self.contract["required"] = [{"name": "fixture", "kind": "directory", "paths": ["directory", "missing"]}]
        self.assertEqual(self.codes(self.run_check()), {"wrong_path_type", "missing_path"})

    def test_fenced_indented_inline_code_and_comments_ignored(self):
        self.write("README.md", "# Good\n```md\n[x](missing1)\n```\n    [x](missing2)\n`[x](missing3)`\n<!-- [x](missing4) -->\n[x](#good)\n")
        result = self.run_check()
        self.assertEqual(result["status"], "passed", result)
        self.assertEqual(result["summary"]["markdown_links_found"], 1)

    def test_unsupported_html_and_nonmarkdown_fragment(self):
        self.write("index.html", "<h1 id='hello'>Hello</h1>")
        self.write("README.md", "# Hello\n[x][id]\n[id]: README.md\n<a id='custom'></a>\n[x](index.html#hello) [y](#hello)\n")
        result = self.run_check()
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(self.codes(result), {"unsupported_html", "non_markdown_fragment", "fragment_incomplete"})

    def test_basic_formatting_unicode_and_setext_heading(self):
        self.write("README.md", "# **Hello** _World_ `snake_case`!\n中文 标题\n===\n[x](#hello-world-snake_case) [y](#中文-标题)\n")
        self.assertEqual(self.run_check()["status"], "passed")

    def test_invalid_percent_encoding(self):
        self.write("README.md", "[a](bad%zz.md) [b](bad%FF.md)\n")
        self.assertEqual(self.codes(self.run_check()), {"invalid_percent_encoding", "invalid_utf8_url"})

    def test_excluded_dependency_and_git_directories_not_scanned(self):
        self.write(".git/never.md", "[x](missing.md)")
        self.write("node_modules/never.md", "[x](missing.md)")
        self.write("README.md", "# Good\n")
        result = self.run_check()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["scope"]["excluded_directories_observed"], [".git", "node_modules"])

    def test_escaped_and_code_underscores_in_headings(self):
        self.write("README.md", r"# \_Literal\_ and `_code_`" + "\n[x](#_literal_-and-_code_)\n")
        self.assertEqual(self.run_check()["status"], "passed")

    def test_plain_ampersand_and_double_spaces_in_heading(self):
        self.write("README.md", "# Alpha &  Beta\n[x](#alpha---beta)\n")
        self.assertEqual(self.run_check()["status"], "passed")

    def test_images_balanced_paths_and_link_titles(self):
        self.write("a(b).svg", "synthetic image placeholder")
        self.write("README.md", '[x](a(b).svg "Example title") ![alt](a(b).svg)\n')
        self.assertEqual(self.run_check()["status"], "passed")

    def test_unclosed_frontmatter_cannot_report_pass(self):
        self.write("README.md", "---\ntitle: fixture\n[x](missing.md)\n")
        result = self.run_check()
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("unsupported_frontmatter", self.codes(result))

    def test_multiline_code_span_is_explicitly_unsupported(self):
        self.write("README.md", "`first line\nsecond line`\n")
        self.assertEqual(self.run_check()["status"], "incomplete")

    def test_malformed_link_is_explicitly_unsupported(self):
        self.write("README.md", "[x](missing.md\n")
        self.assertEqual(self.codes(self.run_check()), {"unsupported_link"})

    def test_literal_array_brackets_are_not_reference_links(self):
        self.write("README.md", "A vector has shape num[2][2..20].\n")
        self.assertEqual(self.run_check()["status"], "passed")

    def test_explicit_links_cannot_read_excluded_directories(self):
        self.write(".git/config.md", "# Private metadata\n")
        self.write("README.md", "[x](.git/config.md#private-metadata)\n")
        result = self.run_check()
        self.assertEqual(result["summary"]["markdown_files_read"], 1)
        self.assertIn("excluded_path", self.codes(result))

    def test_pure_html_breaks_and_external_autolinks(self):
        self.write("README.md", "A<br>B <https://example.invalid/>\n")
        self.assertEqual(self.run_check()["status"], "passed")

    def test_reference_full_collapsed_shortcut_and_case_folding(self):
        self.write("target.md", "# Target\n")
        self.write("README.md", '[a][ID] [other][] [shortcut]\n[id]: target.md#target "Title"\n[Other]: target.md\n[shortcut]: <target.md>\n')
        result = self.run_check()
        self.assertEqual(result["status"], "passed", result)
        self.assertEqual(result["summary"]["local_paths_checked"], 3)

    def test_first_reference_definition_wins(self):
        self.write("target.md", "# Target\n")
        self.write("README.md", "[a][id]\n[id]: target.md\n[id]: missing.md\n")
        self.assertEqual(self.run_check()["status"], "passed")

    def test_linked_image_checks_both_destinations(self):
        self.write("image.svg", "synthetic")
        self.write("README.md", "# Target\n[![alt](image.svg)](#target)\n")
        result = self.run_check()
        self.assertEqual(result["status"], "passed", result)
        self.assertEqual(result["summary"]["local_paths_checked"], 2)
        (self.root / "image.svg").unlink()
        self.assertIn("missing_path", self.codes(self.run_check()))

    def test_multiline_reference_is_reported(self):
        self.write("README.md", "[a][id]\n[id]:\n  target.md\n")
        self.assertEqual(self.codes(self.run_check()), {"unsupported_reference"})

    def test_read_only_and_no_publication_code_execution(self):
        source = self.write("untrusted.py", "raise RuntimeError('This must never be executed')\n")
        self.write("README.md", "[source](untrusted.py)\n")
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        result = self.run_check()
        self.assertEqual(result["status"], "passed")
        self.assertEqual({p.name: p.read_bytes() for p in self.root.iterdir()}, before)
        self.assertFalse(result["scope"]["source_code_executed"])

    def test_individual_checks_can_pass_while_overall_is_incomplete(self):
        self.write("README.md", "[x](index.html#anchor)\n")
        self.write("index.html", "<h1 id='anchor'>Example</h1>")
        result = self.run_check()
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["checks"]["required_structure"]["status"], "passed")
        self.assertEqual(result["checks"]["listed_manifest_hashes"]["status"], "passed")
        self.assertEqual(result["checks"]["markdown_links"]["status"], "incomplete")

    def test_duplicate_json_keys_are_rejected(self):
        self.write("manifest.json", '{"files": {}, "files": {}}')
        self.contract["manifests"] = ["manifest.json"]
        result = self.run_check()
        self.assertIn("manifest_invalid_json", self.codes(result))
        self.assertEqual(result["manifests"][0]["status"], "failed")

    def test_bad_manifest_path_does_not_skip_later_entries(self):
        self.write("a.txt", "a")
        self.write("manifest.json", json.dumps({"files": {"../outside.txt": "0" * 64, "a.txt": hashlib.sha256(b"a").hexdigest()}}))
        self.contract["manifests"] = ["manifest.json"]
        result = self.run_check()
        self.assertEqual(result["manifests"][0]["entries"], 2)
        self.assertEqual(result["manifests"][0]["matched"], 1)
        self.assertEqual(result["manifests"][0]["status"], "failed")

    def test_cli_json_and_exit_codes(self):
        contract = Path(self.tmp.name) / "contract.json"
        contract.write_text(json.dumps(self.contract))
        for content, status, code in (("# Fine\n", "passed", 0), ("[a](missing.md)\n", "failed", 1), ("[a][id]\n[id]:\n  a.md\n", "incomplete", 2)):
            with self.subTest(status=status):
                self.write("README.md", content)
                result = subprocess.run([sys.executable, str(HERE / "check_publication.py"), str(self.root), "--contract", str(contract)], capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], status)
                self.assertIn("publication-check:", result.stderr)


class EmptyAnchorSubset(unittest.TestCase):
    setUp = Fixture.setUp
    tearDown = Fixture.tearDown
    write = Fixture.write
    run_check = Fixture.run_check
    codes = Fixture.codes

    def test_explicit_anchor_and_ordinary_heading(self):
        self.write("README.md", '# Title\n\n<a id="旧锚点-1_"></a>\n\n[old](#旧锚点-1_) [new](#title)\n')
        report = self.run_check()
        self.assertEqual(report["status"], "passed", report["issues"])
        self.assertEqual(report["summary"]["heading_fragments_checked"], 2)

    def test_anchor_boundaries(self):
        for value in ("a", "a" * 128, "中文_123-", "É５"):
            with self.subTest(value=value):
                parsed = checker.markdown('<a id="' + value + '"></a>')
                self.assertTrue(parsed[2])
                self.assertIn(value, parsed[1])

    def test_unsupported_anchor_forms(self):
        for value in ('<a id=""></a>', '<a id="' + 'a' * 129 + '"></a>',
                      '<a id="with space"></a>', '<a id="a.b"></a>',
                      '<a id="e\u0301"></a>', '<a id="&#97;"></a>',
                      '<a id="x" class="y"></a>', '<a id="x">text</a>',
                      "<a id='x'></a>", '<a id="x"/>', '<a name="x"></a>',
                      '<a id="x"></a> text', '> <a id="x"></a>',
                      '<a id="x">\n</a>'):
            with self.subTest(value=value):
                parsed = checker.markdown(value)
                self.assertFalse(parsed[2])
                self.assertIn("unsupported_html", {x[1] for x in parsed[3]})

    def test_commented_decorations_are_outside_strict_subset(self):
        for text in ('<a id="x"></a><!-- comment -->', '<!-- comment --><a id="x"></a>'):
            with self.subTest(text=text):
                parsed = checker.markdown(text)
                self.assertNotIn("x", parsed[1])
        self.assertFalse(checker.markdown('<a id="x"></a><!-- comment -->')[2])

    def test_multiline_contexts_remain_unsupported(self):
        for text in ('![\n\u00a0\n<a id="x"></a>\n\u00a0\n](image.png)',
                     '<![CDATA[\n\n<a id="x"></a>\n\n]]>',
                     '<?pi\n\n<a id="x"></a>\n\n?>',
                     '![\n<a id="x"></a>\n](image.png)',
                     "<div title='\n\n<a id=\"x\"></a>\n\n'>",
                     '<a id="x"></a>\n# Next'):
            with self.subTest(text=text):
                parsed = checker.markdown(text)
                self.assertFalse(parsed[2])
                self.assertIn("unsupported_html", {x[1] for x in parsed[3]})

    def test_anchor_collisions_remain_incomplete(self):
        for text in ('<a id="same"></a>\n\n<a id="same"></a>',
                     '# Same\n\n<a id="same"></a>',
                     '<a id="same"></a>\n\n# Same',
                     '# Same\n# Same\n\n<a id="same-1"></a>'):
            with self.subTest(text=text):
                self.write("README.md", text + '\n\n[link](#same)')
                report = self.run_check()
                self.assertEqual(report["status"], "incomplete")
                self.assertIn("unsupported_anchor_collision", self.codes(report))
                self.assertIn("fragment_incomplete", self.codes(report))
                self.assertNotIn("heading_fragments_checked", report["summary"])

    def test_ignored_anchor_contexts_do_not_create_ids(self):
        for text in ('```html\n<a id="x"></a>\n```',
                     '    <a id="x"></a>', '`<a id="x"></a>`',
                     '<!-- <a id="x"></a> -->',
                     '<!--\n\n<a id="x"></a>\n\n-->',
                     '---\n<a id="x"></a>\n---'):
            with self.subTest(text=text):
                parsed = checker.markdown(text)
                self.assertNotIn("x", parsed[1])

    def test_non_markdown_line_separators_are_unsupported(self):
        for sep in ('\u2028', '\u2029', '\x85', '\v', '\f', '\x1c'):
            parsed = checker.markdown('![' + sep * 2 + '<a id="x"></a>' + sep * 2 + '](image.png)')
            self.assertFalse(parsed[2])
            self.assertIn("unsupported_line_separator", {x[1] for x in parsed[3]})

    def test_ambiguous_indented_html_is_conservatively_unsupported(self):
        for prefix in ('paragraph\n    <textarea>', 'paragraph\n\t<textarea>',
                       'paragraph\n    <!CDATA[', '    <div>'):
            parsed = checker.markdown(prefix + '\n\n<a id="x"></a>\n\n[go](#x)')
            self.assertFalse(parsed[2])
            self.assertIn("unsupported_indented_html", {x[1] for x in parsed[3]})

    def test_indented_code_fences_and_comments_controls(self):
        for prefix in ('    ordinary_code()', '    x = 1',
                       '```html\n    <textarea>\n```',
                       '<!--\n    <textarea>\n-->',
                       '---\n    <textarea>\n---'):
            parsed = checker.markdown(prefix + '\n\n<a id="x"></a>\n\n[go](#x)')
            self.assertTrue(parsed[2], parsed[3])
            self.assertIn("x", parsed[1])
            self.assertNotIn("unsupported_indented_html", {x[1] for x in parsed[3]})

    def test_compact_raw_tags_stay_unsupported(self):
        for tag in ('<script/>', '<img/>', '<Foo.Bar>'):
            parsed = checker.markdown(tag + '\n\n<a id="x"></a>\n\n[go](#x)')
            self.assertFalse(parsed[2])
            self.assertIn("unsupported_html", {x[1] for x in parsed[3]})

    def test_other_html_still_taints_document(self):
        self.write("README.md", '# Title\n\n<a id="old"></a>\n<div id="other"></div>\n[x](#title)')
        report = self.run_check()
        self.assertEqual(report["status"], "incomplete")
        self.assertIn("fragment_incomplete", self.codes(report))

    def test_html_fragments_remain_unsupported_even_with_unique_id(self):
        for html in ('<div id="x"></div>', '<div id="x"></div><script>throw 1</script>'):
            self.write("page.html", html)
            self.write("README.md", '[x](page.html#x)')
            report = self.run_check()
            self.assertEqual(report["status"], "incomplete")
            self.assertIn("non_markdown_fragment", self.codes(report))


if __name__ == "__main__":
    unittest.main()
