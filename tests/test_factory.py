import base64
from contextlib import redirect_stdout, redirect_stderr
import copy
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from factory.__main__ import main, demo_snapshot
from factory.board import render
from factory.github import GitHub, GitHubError, fetch_snapshot, normalize_issue, repository_name
from factory.state import FactoryError, Store, atomic_write


def raw_issue(number=1, status="ready", **overrides):
    return {"number": number, "node_id": "I_%d" % number, "title": "Save an expense",
            "body": "Acceptance: expense persists after reload.", "labels": [{"name": "factory:" + status}],
            "state": "open", "updated_at": "2026-10-20T08:00:00Z", "assignees": [], **overrides}


class FixtureGitHub:
    """A second adapter at the same read interface; no external calls."""
    def __init__(self, issues=None, blockers=None, parents=None, failures=None):
        self.issues = issues if issues is not None else [raw_issue()]
        self.blockers = blockers or {}
        self.parents = parents or {}
        self.failures = failures or {}
        self.calls = []

    def get(self, endpoint, paginate=False):
        self.calls.append(endpoint)
        path = urlsplit(endpoint).path
        for key, status in self.failures.items():
            if key == path:
                raise GitHubError("Fixture failure", status)
        if path == "repos/owner/project":
            return {"full_name": "owner/project"}
        if path == "repos/owner/project/issues":
            state = parse_qs(urlsplit(endpoint).query)["state"][0]
            return copy.deepcopy([i for i in self.issues if i.get("state") == state])
        number = int(path.split("/")[4])
        if path.endswith("/dependencies/blocked_by"):
            return copy.deepcopy(self.blockers.get(number, []))
        if path.endswith("/parent"):
            if number not in self.parents:
                raise GitHubError("No parent", 404)
            return copy.deepcopy(self.parents[number])
        raise AssertionError("Unexpected endpoint: " + endpoint)


class SnapshotTests(unittest.TestCase):
    def test_native_parent_is_not_a_blocker(self):
        client = FixtureGitHub(parents={1: raw_issue(10, "planned")})
        data = fetch_snapshot(client, "owner/project")
        task = data["issues"][0]
        self.assertEqual(task["parent"]["number"], 10)
        self.assertEqual(task["status"], "ready")
        self.assertEqual(task["blockers"], [])

    def test_ready_issue_with_open_native_blocker_is_displayed_blocked(self):
        client = FixtureGitHub(blockers={1: [raw_issue(9)]})
        task = fetch_snapshot(client, "owner/project")["issues"][0]
        self.assertEqual(task["status"], "blocked")
        self.assertEqual(task["reported_status"], "ready")
        self.assertEqual(task["blockers"][0]["number"], 9)

    def test_closed_blocker_does_not_block_a_reported_ready_issue(self):
        client = FixtureGitHub(blockers={1: [raw_issue(9, "done", state="closed")]})
        self.assertEqual(fetch_snapshot(client, "owner/project")["issues"][0]["status"], "ready")

    def test_unreadable_dependencies_never_look_ready(self):
        client = FixtureGitHub(failures={"repos/owner/project/issues/1/dependencies/blocked_by": 403})
        data = fetch_snapshot(client, "owner/project")
        self.assertEqual(data["sync"]["status"], "partial")
        self.assertEqual(data["issues"][0]["status"], "blocked")
        self.assertIn("unknown", " ".join(data["issues"][0]["warnings"]))

    def test_missing_parent_is_normal_but_a_parent_access_error_is_visible(self):
        task = fetch_snapshot(FixtureGitHub(), "owner/project")["issues"][0]
        self.assertEqual(task["relations"], "loaded")
        self.assertEqual(task["warnings"], [])
        client = FixtureGitHub(failures={"repos/owner/project/issues/1/parent": 403})
        task = fetch_snapshot(client, "owner/project")["issues"][0]
        self.assertEqual(task["relations"], "partial")

    def test_pull_requests_are_not_board_issues(self):
        client = FixtureGitHub(issues=[raw_issue(), raw_issue(2, pull_request={"url": "unused"})])
        self.assertEqual([i["number"] for i in fetch_snapshot(client, "owner/project")["issues"]], [1])

    def test_conflicting_status_labels_require_attention(self):
        task = normalize_issue(raw_issue(labels=[{"name": "factory:ready"}, {"name": "factory:done"}]), "owner/project")
        self.assertEqual(task["status"], "blocked")
        self.assertIn("Conflicting", task["warnings"][0])

    def test_closed_is_reported_not_verified_complete(self):
        data = fetch_snapshot(FixtureGitHub(issues=[raw_issue(state="closed", labels=[])]), "owner/project")
        self.assertEqual(data["issues"][0]["status"], "done")
        self.assertEqual(data["issues"][0]["verification"], "not_checked")
        self.assertFalse(data["execution_enabled"])

    def test_closed_history_and_all_label_filters_are_explicit(self):
        client = FixtureGitHub()
        data = fetch_snapshot(client, "owner/project", closed_days=7, labels=["enhancement", "ready-for-agent"])
        calls = [parse_qs(urlsplit(x).query) for x in client.calls if urlsplit(x).path == "repos/owner/project/issues"]
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]["labels"], ["enhancement,ready-for-agent"])
        self.assertIn("since", calls[1])
        self.assertEqual(data["scope"]["closed_days"], 7)

    def test_transition_between_open_and_closed_queries_is_deduplicated(self):
        class MovingIssue(FixtureGitHub):
            def get(self, endpoint, paginate=False):
                if urlsplit(endpoint).path.endswith("/issues"):
                    state = parse_qs(urlsplit(endpoint).query)["state"][0]
                    return [raw_issue(state=state, updated_at="2026-10-21T09:00:00Z" if state == "closed" else "2026-10-20T09:00:00Z")]
                return super().get(endpoint, paginate)
        data = fetch_snapshot(MovingIssue(), "owner/project")
        self.assertEqual(len(data["issues"]), 1)
        self.assertEqual(data["issues"][0]["state"], "closed")

    def test_repository_redirect_does_not_silently_rebind(self):
        class Redirected(FixtureGitHub):
            def get(self, endpoint, paginate=False):
                return {"full_name": "someone/else"}
        with self.assertRaises(FactoryError):
            fetch_snapshot(Redirected(), "owner/project")

    def test_malformed_issue_records_fail_with_a_clear_error(self):
        for data in (raw_issue(body={"not": "text"}), raw_issue(state="invalid"), raw_issue(labels=None), raw_issue(assignees=None)):
            with self.subTest(data=data), self.assertRaises(FactoryError):
                normalize_issue(data, "owner/project")


class AdapterTests(unittest.TestCase):
    def test_paginated_read_uses_get_and_collects_every_page(self):
        with patch("factory.github.subprocess.run", return_value=subprocess.CompletedProcess([], 0, '[[{"number":1}],[{"number":2}]]', "")) as run:
            data = GitHub().get("repos/owner/project/issues", paginate=True)
        self.assertEqual([i["number"] for i in data], [1, 2])
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("--method") + 1], "GET")
        self.assertIn("--paginate", command)
        self.assertIn("--slurp", command)
        self.assertEqual(command[command.index("--hostname") + 1], "github.com")

    def test_stderr_cannot_leak_into_cached_errors(self):
        with patch("factory.github.subprocess.run", return_value=subprocess.CompletedProcess([], 1, "", "secret-fixture-value (HTTP 401)")):
            with self.assertRaises(GitHubError) as cm:
                GitHub().get("repos/owner/project")
        self.assertNotIn("secret-fixture-value", str(cm.exception))
        self.assertEqual(cm.exception.status, 401)

    def test_timeout_is_actionable(self):
        with patch("factory.github.subprocess.run", side_effect=subprocess.TimeoutExpired("gh", 1)):
            with self.assertRaisesRegex(FactoryError, "timeout"):
                GitHub().get("repos/owner/project")

    def test_malformed_response_does_not_turn_into_an_empty_board(self):
        for value in ("not json", '{"not":"pages"}', '[{"not":"a page"}]'):
            with self.subTest(value=value), patch("factory.github.subprocess.run", return_value=subprocess.CompletedProcess([], 0, value, "")):
                with self.assertRaises(FactoryError):
                    GitHub().get("repos/owner/project/issues", paginate=True)

    def test_unsafe_repository_strings_are_rejected(self):
        for value in ("../project", "owner/..", "https://github.com/owner/project", "owner/project?state=all", "owner/project/extra", "--help"):
            with self.subTest(value=value), self.assertRaises(FactoryError):
                repository_name(value)


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)
        self.store = Store(self.directory)

    def tearDown(self):
        self.tmp.cleanup()

    def command(self, *args, client=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("factory.__main__.GitHub", return_value=client or FixtureGitHub()), redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["--state-dir", str(self.directory), *args])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_first_sync_produces_reopenable_snapshot_and_self_contained_board(self):
        code, out, err = self.command("sync", "--repo", "owner/project")
        self.assertEqual(code, 0, err)
        data = Store(self.directory).load()
        self.assertEqual(data["repository"], "owner/project")
        self.assertEqual(data["issues"][0]["title"], "Save an expense")
        self.assertTrue((self.directory / "board.html").exists())
        self.assertIn("snapshot_refreshed", (self.directory / "events.jsonl").read_text())

    def test_failed_refresh_preserves_cards_and_last_success_and_marks_stale(self):
        self.command("sync", "--repo", "owner/project")
        before = self.store.load()
        code, out, err = self.command("sync", client=FixtureGitHub(failures={"repos/owner/project": 403}))
        self.assertEqual(code, 1)
        after = self.store.load()
        self.assertEqual(after["issues"], before["issues"])
        self.assertEqual(after["last_successful_sync"], before["last_successful_sync"])
        self.assertEqual(after["sync"]["status"], "error")
        payload = re.search(r'atob\("([A-Za-z0-9+/=]+)"\)', (self.directory / "board.html").read_text()).group(1)
        self.assertEqual(json.loads(base64.b64decode(payload))["sync"]["status"], "error")

    def test_malformed_remote_issue_keeps_previous_board(self):
        self.command("sync", "--repo", "owner/project")
        before = self.store.load()
        code, out, err = self.command("sync", client=FixtureGitHub(issues=[raw_issue(labels=None)]))
        self.assertEqual(code, 1)
        self.assertEqual(self.store.load()["issues"], before["issues"])
        self.assertEqual(self.store.load()["sync"]["status"], "error")

    def test_binding_cannot_switch_repo_or_mix_demo_with_live_data(self):
        self.command("sync", "--repo", "owner/project")
        before = (self.directory / "board.json").read_bytes()
        for args in (("sync", "--repo", "other/project"), ("demo",)):
            self.assertEqual(self.command(*args)[0], 1)
            self.assertEqual((self.directory / "board.json").read_bytes(), before)

    def test_no_target_does_not_guess_a_repository(self):
        code, out, err = self.command("sync")
        self.assertEqual(code, 1)
        self.assertIn("No repository", err)
        self.assertFalse((self.directory / "board.json").exists())

    def test_label_scope_is_remembered_and_can_be_cleared(self):
        self.command("sync", "--repo", "owner/project", "--label", "enhancement")
        client = FixtureGitHub()
        self.assertEqual(self.command("sync", client=client)[0], 0)
        self.assertEqual(self.store.load()["scope"]["labels"], ["enhancement"])
        self.assertEqual(self.command("sync", "--all-labels")[0], 0)
        self.assertEqual(self.store.load()["scope"]["labels"], [])

    def test_a_second_controller_is_refused_while_lock_is_held(self):
        with self.store.lock():
            code, out, err = self.command("demo")
        self.assertEqual(code, 1)
        self.assertIn("Another factory command", err)
        self.assertFalse((self.directory / "board.json").exists())

    def test_interrupted_atomic_replace_keeps_previous_snapshot(self):
        self.command("demo")
        before = (self.directory / "board.json").read_bytes()
        with patch("factory.state.os.replace", side_effect=OSError("simulated interrupted replacement")):
            with self.assertRaises(OSError):
                self.store.save(demo_snapshot())
        self.assertEqual((self.directory / "board.json").read_bytes(), before)
        self.assertEqual(list(self.directory.glob(".board.json.*")), [])

    def test_cached_board_renders_without_network_access(self):
        self.command("demo")
        (self.directory / "board.html").unlink()
        with patch("factory.github.subprocess.run", side_effect=AssertionError("Network access not allowed")):
            self.assertEqual(self.command("board")[0], 0)
        self.assertTrue((self.directory / "board.html").exists())

    def test_invalid_saved_schema_is_preserved(self):
        path = self.directory / "board.json"
        path.write_text('{"schema_version":99}')
        code, out, err = self.command("demo")
        self.assertEqual(code, 1)
        self.assertIn("Unsupported", err)
        self.assertEqual(path.read_text(), '{"schema_version":99}')

    def test_untrusted_issue_content_round_trips_without_becoming_markup(self):
        data = demo_snapshot()
        payload = '</script><script>window.injectionExecuted=true</script><img src=x onerror="alert(1)">'
        data["issues"][0]["title"] = payload
        data["issues"][0]["body"] = "Dads' expenses: \u00a3\u20ac\U0001f4b0 " + payload
        html = render(data)
        self.assertNotIn(payload, html)
        encoded = re.search(r'atob\("([A-Za-z0-9+/=]+)"\)', html).group(1)
        decoded = json.loads(base64.b64decode(encoded))
        self.assertEqual(decoded["issues"][0]["body"], data["issues"][0]["body"])


if __name__ == "__main__":
    unittest.main()
