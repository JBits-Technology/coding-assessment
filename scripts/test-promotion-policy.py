"""Exercise the workflow's actual Python code with mocked GitHub responses."""
import ast
import copy
import io
import json
import os
from pathlib import Path
import tempfile
import textwrap
import unittest
import urllib.request
from contextlib import redirect_stdout
from unittest.mock import patch

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/promotion-policy.yml"
shell = textwrap.dedent(WORKFLOW.read_text().split("run: |\n", 1)[1])
CODE = shell.split("python3 - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
ast.parse(CODE)
REPO = "JBits-Technology/api-gateway"
HEAD = "a" * 40


class PromotionPolicyTests(unittest.TestCase):
    def metadata(self, base="dev", source="fix/example", merge="b" * 40):
        return {
            "number": 123, "state": "open", "mergeable": True, "merge_commit_sha": merge,
            "head": {"ref": source, "sha": HEAD, "repo": {"id": 1}},
            "base": {"ref": base, "repo": {"id": 1, "full_name": REPO}},
        }

    def execute(self, metadata, pending=False, peers=None):
        posted, calls = [], []
        def urlopen(req, timeout=0):
            calls.append(req)
            if req.method == "POST":
                posted.append((req.full_url, json.loads(req.data)))
                return io.BytesIO(b"{}")
            if "/pulls?" in req.full_url:
                values = peers if peers is not None else ([metadata] if metadata["state"] == "open" else [])
                return io.BytesIO(json.dumps(values).encode())
            if peers:
                target = int(req.full_url.rsplit("/", 1)[1])
                if target != metadata["number"]:
                    value = next(pr for pr in peers if pr["number"] == target)
                    return io.BytesIO(json.dumps(value).encode())
            value = copy.deepcopy(metadata)
            if pending and len(calls) == 1:
                value.update(mergeable=None, merge_commit_sha=None)
            return io.BytesIO(json.dumps(value).encode())
        with tempfile.TemporaryDirectory() as temporary:
            event = Path(temporary) / "event.json"
            event.write_text('{"number": 123}')
            environment = {
                "GITHUB_REPOSITORY": REPO,
                "GITHUB_API_URL": "https://api.github.com",
                "GITHUB_EVENT_PATH": str(event),
                "GH_TOKEN": "test-placeholder",
                "GITHUB_SERVER_URL": "https://github.com",
                "GITHUB_RUN_ID": "123",
            }
            with patch.dict(os.environ, environment), \
                 patch.object(urllib.request, "urlopen", urlopen), \
                 patch("time.sleep"), redirect_stdout(io.StringIO()):
                exit_code = 0
                try:
                    exec(compile(CODE, "promotion-workflow", "exec"), {})
                except SystemExit as error:
                    exit_code = error.code
        return exit_code, posted

    def assert_status(self, metadata, state, pending=False):
        code, posted = self.execute(metadata, pending)
        self.assertEqual(len(posted), 1)
        url, payload = posted[0]
        self.assertTrue(url.endswith("/statuses/" + metadata["merge_commit_sha"]))
        self.assertFalse(url.endswith("/statuses/" + HEAD))
        self.assertEqual(payload["context"], "Promotion Policy")
        self.assertEqual(payload["state"], state)
        self.assertEqual(code == 0, state == "success")
        return url

    def test_shared_head_results_are_isolated(self):
        accepted = self.assert_status(self.metadata(), "success")
        rejected = self.assert_status(self.metadata(base="main", merge="c" * 40), "failure")
        self.assertNotEqual(accepted, rejected)

    def test_retarget_uses_current_merge_commit(self):
        original = self.assert_status(self.metadata(), "success")
        retargeted = self.assert_status(self.metadata(base="uat", merge="d" * 40), "failure")
        self.assertNotEqual(original, retargeted)

    def test_valid_promotions(self):
        for base, source in [("uat", "dev"), ("main", "uat")]:
            with self.subTest(base=base):
                self.assert_status(self.metadata(base, source), "success")

    def test_fork_rejected(self):
        metadata = self.metadata()
        metadata["head"]["repo"]["id"] = 2
        self.assert_status(metadata, "failure")

    def test_pending_merge_calculation_is_retried(self):
        self.assert_status(self.metadata(), "success", pending=True)

    def test_closed_conflicted_or_unavailable_does_not_publish_success(self):
        for changes in [
            {"state": "closed"},
            {"mergeable": False},
            {"mergeable": None, "merge_commit_sha": None},
            {"mergeable": True, "merge_commit_sha": "invalid"},
        ]:
            with self.subTest(changes=changes):
                metadata = self.metadata()
                metadata.update(changes)
                code, posted = self.execute(metadata)
                self.assertEqual(posted, [])
                if metadata["state"] == "open":
                    self.assertNotEqual(code, 0)

    def test_identical_test_merge_sha_cannot_publish_ambiguous_success(self):
        accepted = self.metadata(base="uat", source="dev")
        rejected = self.metadata(base="main", source="dev")
        rejected["number"] = 124
        code, posted = self.execute(accepted, peers=[accepted, rejected])
        self.assertNotEqual(code, 0)
        self.assertEqual(posted[0][1]["state"], "failure")
        self.assertIn("shared", posted[0][1]["description"])

    def test_closing_duplicate_refreshes_remaining_pr(self):
        closed = self.metadata(base="main", source="dev")
        closed["state"] = "closed"
        remaining = self.metadata(base="uat", source="dev")
        remaining["number"] = 124
        code, posted = self.execute(closed, peers=[remaining])
        self.assertEqual(code, 0)
        self.assertEqual(len(posted), 1)
        self.assertEqual(posted[0][1]["state"], "success")


if __name__ == "__main__":
    unittest.main()

