"""Offline guardrails for ledger reporting, without API calls or private caches."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("build_ledger", Path(__file__).resolve().parents[1] / "scripts/build_ledger.py")
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)

class LedgerTests(unittest.TestCase):
    def run_case(self, claims):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs").mkdir()
            old_root, old_claims = ledger.ROOT, ledger.CLAIMS
            ledger.ROOT, ledger.CLAIMS = root, claims
            out = io.StringIO()
            try:
                with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as caught:
                    ledger.main()
                return caught.exception.code, out.getvalue(), (root / "docs/claims_ledger.md").read_text()
            finally:
                ledger.ROOT, ledger.CLAIMS = old_root, old_claims

    def test_match_and_skipped_are_distinct(self):
        code, out, text = self.run_case([
            ("x", "matching", "1", lambda: "1", "tracked.csv"),
            ("x", "cache", "1", lambda: None, "local.jsonl"),
        ])
        self.assertEqual(code, 0)
        self.assertIn("1/1 checkable claims match; 1 need the local API cache", out)
        self.assertIn("not checkable here", text)
        self.assertIn("does not parse the DOCX/PDF", text)

    def test_mismatch_fails(self):
        code, out, text = self.run_case([("x", "mismatch", "1", lambda: "2", "tracked.csv")])
        self.assertEqual(code, 1)
        self.assertIn("MISMATCH", text)
        self.assertIn("0/1 checkable claims match", out)

if __name__ == "__main__":
    unittest.main()
