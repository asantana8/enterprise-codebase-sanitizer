import os
from pathlib import Path
import stat
import tempfile
import unittest

from sanitizer import build_context, clean_text, main, write_context


class SanitizerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        self.root.mkdir()
        self.output = Path(self.temporary.name) / "context.md"

    def put(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_filters_and_deterministic_context(self):
        self.put("src/main.py", "print('hello')  \n\n\n# keep comments\n")
        self.put("node_modules/dep.js", "dependency")
        self.put("nested/BUILD/artifact.txt", "artifact")
        self.put(".env.example", "DO_NOT_EXPORT=example")
        self.put("package-lock.json", "lockfile")
        self.put(".aws/config", "credentials")
        self.put("debug.log", "log")
        (self.root / "binary.dat").write_bytes(b"\x00\xff")
        self.put("large.txt", "x" * 501)
        document, stats = build_context(self.root, self.output, max_file_bytes=500)
        self.assertIn("print('hello')\n\n# keep comments", document)
        for forbidden in ("dependency", "artifact", "DO_NOT_EXPORT", "lockfile", "credentials"):
            self.assertNotIn(forbidden, document)
        self.assertEqual(stats["included"], 1)
        self.assertEqual(stats["binary"], 1)
        self.assertEqual(stats["oversized"], 1)
        self.assertEqual(build_context(self.root, self.output, 500), (document, stats))

    def test_secret_files_are_omitted_entirely(self):
        cases = [
            'password = """\nmultiline-value\n"""',
            '{"api_key": "example-value"}',
            "-----BEGIN RSA PRIVATE KEY-----\nprivate-material",
            "https://" + "example-user" + ":" + "example-pass" + "@host.test",
            "ghp_" + "a" * 36,
            "AKIA" + "A" * 16,
            ".".join(("eyJ" + "a" * 12, "b" * 12, "c" * 12)),
            "Authorization: ******",
            "accessToken:\n  nested-value",
        ]
        for index, content in enumerate(cases):
            with self.subTest(content=content):
                self.assertIsNone(clean_text(content))
            self.put(f"secret{index}.txt", content)
        self.put("safe.py", "print('safe')")
        document, stats = build_context(self.root, self.output)
        self.assertEqual(stats["secret_files"], len(cases))
        self.assertNotIn("secret0.txt", document)
        self.assertNotIn("multiline-value", document)
        self.assertIn("print('safe')", document)

    def test_symlinks_special_files_and_non_utf8(self):
        outside = Path(self.temporary.name) / "outside.txt"
        outside.write_text("outside confidential", encoding="utf-8")
        (self.root / "link.txt").symlink_to(outside)
        (self.root / "linked-dir").symlink_to(outside.parent, target_is_directory=True)
        (self.root / "bad.txt").write_bytes(b"\xff")
        os.mkfifo(self.root / "pipe")
        document, stats = build_context(self.root, self.output)
        self.assertNotIn("outside confidential", document)
        self.assertEqual(stats["symlink"], 2)
        self.assertEqual(stats["non_utf8"], 1)
        self.assertEqual(stats["non_regular"], 1)

    def test_budget_and_markdown_fences(self):
        self.put("a.md", "```\nexample\n```")
        self.put("b.txt", "b" * 200)
        document, stats = build_context(self.root, self.output, max_context_bytes=100)
        self.assertIn("````\n```\nexample\n```\n````", document)
        self.assertEqual(stats["included"], 1)
        self.assertEqual(stats["budget"], 1)

    def test_compaction_preserves_initial_indentation(self):
        self.assertEqual(clean_text("\n\n    indented  \n\n\nnext\n"), "    indented\n\nnext")

    def test_secure_output_and_no_accidental_overwrite(self):
        write_context(self.output, "first")
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o600)
        with self.assertRaises(ValueError):
            write_context(self.output, "second")
        self.assertEqual(self.output.read_text(), "first")
        write_context(self.output, "second", force=True)
        self.assertEqual(self.output.read_text(), "second")
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o600)
        self.assertEqual(list(self.output.parent.glob(".sanitizer-*")), [])
        link = self.root / "output.md"
        link.symlink_to(self.output)
        with self.assertRaises(ValueError):
            write_context(link, "unsafe", force=True)
        self.assertEqual(self.output.read_text(), "second")

    def test_cli_and_output_excluded_on_rerun(self):
        self.put("a.py", "print('hello')")
        output = self.root / "context.md"
        self.assertEqual(main([str(self.root), "-o", str(output)]), 0)
        original = output.read_text()
        self.assertEqual(main([str(self.root), "-o", str(output), "--force"]), 0)
        self.assertEqual(output.read_text(), original)

    def test_invalid_root_and_limits(self):
        with self.assertRaises(ValueError):
            build_context(self.root / "missing", self.output)
        with self.assertRaises(ValueError):
            build_context(self.root, self.output, max_file_bytes=0)
        with self.assertRaises(SystemExit) as result:
            main([str(self.root), "-o", str(self.output), "--max-context-bytes", "-1"])
        self.assertEqual(result.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
