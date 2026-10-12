import tempfile
from pathlib import Path
import unittest
from scope_desk import Desk, validate_analysis


def fake(message, scopes):
    return {"items": [{"request_quote": message, "scope_id": None,
        "assessment": "clarify", "explanation": "Confirm the request."}]}, {"type": "offline test mock"}


class DeskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "desk.sqlite"
        self.desk = Desk(self.path)
        self.a = self.desk.create("A", ["One landing page"])
        self.b = self.desk.create("B", ["Two articles"])

    def tearDown(self):
        self.desk.close()
        self.tmp.cleanup()

    def test_provider_only_receives_selected_project(self):
        seen = []
        def infer(message, scopes):
            seen.extend(scopes)
            return fake(message, scopes)
        result = self.desk.draft(self.a, "Add checkout", infer)
        self.assertEqual([x["text"] for x in seen], ["One landing page"])
        self.assertEqual(result["state"], "REVIEW")
        self.assertEqual(self.desk.db.execute("SELECT count(*) FROM receipts").fetchone()[0], 0)
        with self.assertRaises(ValueError): self.desk.get_draft(self.b, result["id"])
        with self.assertRaises(ValueError): self.desk.approve(self.b, result["id"], True)

    def test_explicit_review_and_replay_survive_restart(self):
        result = self.desk.draft(self.a, "Add checkout", fake)
        with self.assertRaises(ValueError): self.desk.approve(self.a, result["id"])
        self.assertFalse(self.desk.approve(self.a, result["id"], True)["replay"])
        self.desk.close(); self.desk = Desk(self.path)
        self.assertTrue(self.desk.approve(self.a, result["id"], True)["replay"])
        self.assertEqual(self.desk.db.execute("SELECT count(*) FROM receipts").fetchone()[0], 1)

    def test_scope_update_invalidates_pending_draft(self):
        result = self.desk.draft(self.a, "Add checkout", fake)
        self.desk.amend_scope(self.a, 1, ["One landing page", "Checkout"])
        with self.assertRaises(ValueError): self.desk.approve(self.a, result["id"], True)

    def test_scope_change_during_model_call_discards_result(self):
        def infer(message, scopes):
            self.desk.amend_scope(self.a, 1, ["Changed scope"])
            return fake(message, scopes)
        with self.assertRaises(ValueError): self.desk.draft(self.a, "Add checkout", infer)
        self.assertEqual(self.desk.db.execute("SELECT count(*) FROM drafts").fetchone()[0], 0)

    def test_persistent_budget_counts_failures(self):
        def fail(message, scopes): raise ValueError("Provider failed")
        for _ in range(10):
            with self.assertRaises(ValueError): self.desk.draft(self.a, "Add checkout", fail)
        self.desk.close(); self.desk = Desk(self.path)
        with self.assertRaises(ValueError): self.desk.draft(self.a, "Add checkout", fake)

    def test_grounding_and_schema_reject_invented_refs_and_quotes(self):
        scopes = self.desk.project(self.a)["scopes"]
        value, _ = fake("Add checkout", scopes)
        item = value["items"][0]
        for bad in ({**item, "request_quote": "Do free work"},
                    {**item, "assessment": "included"},
                    {**item, "scope_id": "foreign-project-item"},
                    {**item, "fee": 100}, {**item, "assessment": "approved"}):
            with self.assertRaises(ValueError): validate_analysis({"items": [bad]}, "Add checkout", scopes)
        with self.assertRaises(ValueError): validate_analysis({"items": [item, item]}, "Add checkout", scopes)

    def test_provider_failure_never_creates_draft(self):
        def bad(message, scopes): return {"items": []}, {}
        with self.assertRaises(ValueError): self.desk.draft(self.a, "Add checkout", bad)
        self.assertEqual(self.desk.db.execute("SELECT count(*) FROM drafts").fetchone()[0], 0)

    def test_export_requires_review_and_cannot_use_another_project(self):
        result = self.desk.draft(self.a, "Add checkout", fake)
        with self.assertRaises(ValueError): self.desk.export(self.a, result["id"])
        self.desk.approve(self.a, result["id"], True)
        text = self.desk.export(self.a, result["id"])
        self.assertIn("CLARIFY: Add checkout", text)
        self.assertIn("No prices or work commitments", text)
        with self.assertRaises(ValueError): self.desk.export(self.b, result["id"])


if __name__ == "__main__": unittest.main()
