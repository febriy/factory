"""Exercise inactive harness templates in disposable Git repositories."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "skills/software-factory/assets/repo-harness"
HOOK = ".codex/hooks/factory_harness.py"
spec = importlib.util.spec_from_file_location("harness", ASSETS / HOOK)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="factory harness ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        shutil.copytree(ASSETS, self.root, dirs_exist_ok=True)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Harness Test")
        self.write("src/feature.py", "initial\n")
        self.write("db/migrations/001.sql", "initial\n")
        self.write("package-lock.json", "{}\n")
        self.write("tests/scenarios/journey.txt", "holdout\n")
        self.configure("run_check smoke true")
        self.commit()
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.cwd = self.root / "src"

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], text=True,
                              capture_output=True, check=True)

    def write(self, path, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value)

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")

    def configure(self, body):
        template = (ASSETS / "scripts/agent-check.sh").read_text()
        start = template.index("product_checks() {")
        end = template.index('\n}\n', start) + 2
        self.write("scripts/agent-check.sh", template[:start] + "product_checks() {\n" + body +
                   "\n}" + template[end:])

    def command(self, *args, event=None):
        return subprocess.run([sys.executable, str(self.root / HOOK), *args], cwd=self.cwd,
                              input=json.dumps(event) if event is not None else None,
                              text=True, capture_output=True)

    def arm(self, *extra):
        result = self.command("arm", "--session", "test-session", "--base", self.base, *extra)
        self.assertEqual(result.returncode, 0, result.stderr)

    def event(self, **overrides):
        return {"session_id": "test-session", "cwd": str(self.cwd), "turn_id": "turn-1", **overrides}

    def stop(self, **overrides):
        result = self.command("stop", event=self.event(hook_event_name="Stop", **overrides))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def patch_event(self, *lines):
        return self.event(tool_name="apply_patch", hook_event_name="PreToolUse",
                          tool_input={"command": "*** Begin Patch\n" + "\n".join(lines) + "\n*** End Patch"})

    def decision(self, event):
        result = self.command("pre-tool", event=event)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_unconfigured_template_fails_instead_of_passing(self):
        self.write("scripts/agent-check.sh", (ASSETS / "scripts/agent-check.sh").read_text())
        result = subprocess.run(["bash", str(self.root / "scripts/agent-check.sh")], cwd=self.cwd,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("NOT CONFIGURED", result.stderr)

    def test_check_aggregates_failures_and_runs_from_subdirectory(self):
        self.configure('run_check failure bash -c "exit 7"\nrun_check root test -f src/feature.py')
        result = subprocess.run(["bash", str(self.root / "scripts/agent-check.sh"), "full"],
                                cwd=self.cwd, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("exit 7", result.stderr)
        self.assertIn("PASS: root", result.stdout)
        self.assertIn("1 of 2", result.stderr)

    def test_empty_check_configuration_and_unknown_mode_fail(self):
        self.configure("true")
        for mode in ("fast", "typo"):
            result = subprocess.run(["bash", str(self.root / "scripts/agent-check.sh"), mode],
                                    cwd=self.cwd, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)

    def test_check_without_command_is_configuration_failure(self):
        self.configure("run_check missing-command\nrun_check smoke true")
        result = subprocess.run(["bash", str(self.root / "scripts/agent-check.sh")],
                                cwd=self.cwd, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires a label and command", result.stderr)

    def test_planning_does_not_run_checks_even_with_dirty_checkout(self):
        self.configure('touch should-not-run; run_check smoke false')
        self.assertEqual(self.stop(), {})
        self.assertFalse((self.root / "should-not-run").exists())

    def test_armed_but_unchanged_task_skips_checks(self):
        self.arm()
        self.assertEqual(self.stop(), {})

    def test_repair_cap_survives_changing_turn_ids_and_repeated_arming(self):
        # A dirty allowed source file triggers a failing existing native command.
        self.configure("run_check smoke false")
        self.commit()
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.arm()
        self.write("src/feature.py", "broken\n")
        for i in range(3):
            self.assertEqual(self.stop(turn_id="continuation-%d" % i)["decision"], "block")
            self.arm()
        result = self.stop(turn_id="continuation-4")
        self.assertNotIn("decision", result)
        self.assertIn("repair limit reached", result["systemMessage"])
        self.assertIn("FAILED", result["systemMessage"])

    def test_passing_checks_do_not_cache_later_failures(self):
        self.configure("run_check behavior bash -c 'test ! -e src/broken'")
        self.commit()
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.arm()
        self.write("src/feature.py", "changed\n")
        self.assertIn("passed", self.stop()["systemMessage"])
        self.write("src/broken", "broken")
        self.assertEqual(self.stop()["decision"], "block")

    def test_disarm_leaves_acceptance_unchanged_and_preserves_files(self):
        self.arm()
        self.write("src/feature.py", "unfinished\n")
        result = self.command("disarm", "--session", "test-session")
        self.assertIn("acceptance unchanged", result.stdout)
        self.assertEqual(self.stop(), {})
        self.assertEqual((self.root / "src/feature.py").read_text(), "unfinished\n")

    def test_protected_patch_paths_include_rename_destinations(self):
        for path in ("../.env.local", "../package-lock.json", "../db/migrations/001.sql",
                     "../tests/scenarios/journey.txt", "../.codex/hooks.json"):
            with self.subTest(path=path):
                result = self.decision(self.patch_event("*** Update File: " + path, "@@", "-a", "+b"))
                self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")
        result = self.decision(self.patch_event("*** Update File: feature.py",
                                               "*** Move to: ../tests/scenarios/new.txt", "@@", "-a", "+b"))
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_new_migration_and_ordinary_source_are_allowed(self):
        for path in ("feature.py", "../db/migrations/002.sql"):
            self.assertEqual(self.decision(self.patch_event("*** Add File: " + path, "+new")), {})

    def test_symlink_alias_to_protected_file_is_denied(self):
        (self.cwd / "alias").symlink_to(self.root / "package-lock.json")
        result = self.decision(self.patch_event("*** Update File: alias", "@@", "-a", "+b"))
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_outside_checkout_and_unparseable_patches_are_denied(self):
        for event in (self.patch_event("*** Add File: ../../outside", "+bad"),
                      self.event(tool_name="apply_patch", tool_input={"command": "invalid"})):
            self.assertEqual(self.decision(event)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_exact_exception_requires_reason_and_does_not_allow_siblings(self):
        args = ("arm", "--session", "test-session", "--base", self.base,
                "--allow-path", "package-lock.json")
        self.assertEqual(self.command(*args).returncode, 2)
        self.arm("--allow-path", "package-lock.json", "--reason", "Approved dependency task #1")
        self.assertEqual(self.decision(self.patch_event("*** Update File: ../package-lock.json", "@@", "-a", "+b")), {})
        self.assertEqual(self.decision(self.patch_event("*** Add File: ../yarn.lock", "+new"))
                         ["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_guard_detects_committed_shell_edits_and_policy_weakening(self):
        self.write("package-lock.json", "shell changed\n")
        self.write(".codex/hooks/protected-paths.json", '{"always": [], "existing": []}')
        self.commit()
        result = self.command("guard", "--base", self.base)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("package-lock.json", result.stderr)
        self.assertIn("protected-paths.json", result.stderr)

    def test_guard_catches_deleting_or_renaming_protected_source(self):
        self.git("mv", "package-lock.json", "src/former-lock")
        result = self.command("guard", "--base", self.base)
        self.assertEqual(result.returncode, 2)
        self.assertIn("package-lock.json", result.stderr)

    def test_guard_allows_exact_authorized_dependency_change(self):
        self.write("package-lock.json", "changed\n")
        result = self.command("guard", "--base", self.base, "--allow-path", "package-lock.json",
                              "--reason", "Maintainer approved dependency update")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_stop_guard_catches_shell_edits_before_check_script(self):
        self.arm()
        self.write("package-lock.json", "changed\n")
        self.assertIn("Protected paths changed", self.stop()["reason"])

    def test_stop_reports_malformed_input_without_infinite_continuation(self):
        for payload in ("bad json", "[]"):
            result = subprocess.run([sys.executable, str(self.root / HOOK), "stop"],
                                    input=payload, text=True, capture_output=True, cwd=self.cwd)
            output = json.loads(result.stdout)
            self.assertNotIn("decision", output)
            self.assertIn("unavailable", output["systemMessage"])

    def test_sessions_are_isolated_and_state_is_untracked(self):
        self.arm()
        self.write("src/feature.py", "changed\n")
        self.assertEqual(self.stop(session_id="other-session"), {})
        self.assertNotIn("factory-harness", self.git("status", "--porcelain").stdout)

    def test_linked_worktree_does_not_inherit_main_checkout_session(self):
        self.arm()
        linked = self.root / "linked-checkout"
        self.git("worktree", "add", "--detach", str(linked), self.base)
        event = self.event(cwd=str(linked / "src"))
        result = subprocess.run([sys.executable, str(linked / HOOK), "stop"], cwd=linked,
                                input=json.dumps(event), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {})

    def test_corrupt_state_reports_unavailable_and_can_be_disarmed(self):
        self.arm()
        state_dir = Path(self.git("rev-parse", "--path-format=absolute", "--git-path", "factory-harness").stdout.strip())
        next(state_dir.glob("*.json")).write_text("broken")
        self.assertIn("unavailable", self.stop()["systemMessage"])
        self.assertEqual(self.command("disarm", "--session", "test-session").returncode, 0)
        self.arm()

    def test_rearming_different_scope_requires_explicit_handoff(self):
        self.arm()
        result = self.command("arm", "--session", "test-session", "--base", self.base,
                              "--allow-path", "package-lock.json", "--reason", "Other task")
        self.assertEqual(result.returncode, 2)
        self.assertIn("different scope", result.stderr)

    def test_timeout_kills_check_process_group_and_requests_bounded_repair(self):
        self.arm()
        self.write("src/feature.py", "changed\n")
        with patch.object(harness.subprocess, "Popen") as popen, patch.object(harness.os, "killpg") as killpg:
            process = popen.return_value
            process.pid = 12345
            process.wait.side_effect = [subprocess.TimeoutExpired("check", 120), 0]
            with patch.object(harness, "changed_paths", return_value=["src/feature.py"]), \
                 patch.object(harness, "protected", return_value=[]), \
                 patch.object(harness, "git", return_value=str(self.root / ".git/factory-harness")):
                result = harness.stop(self.root, self.event())
            self.assertIn("exceeded", result["reason"])
            killpg.assert_called_once_with(12345, harness.signal.SIGKILL)

    def test_hook_manifest_commands_work_from_subdirectory_with_spaces(self):
        config = json.loads((self.root / ".codex/hooks.json").read_text())
        for event_name, groups in config["hooks"].items():
            command = groups[0]["hooks"][0]["command"]
            event = self.event(hook_event_name=event_name, tool_name="apply_patch",
                               tool_input={"command": "*** Begin Patch\n*** Update File: feature.py\n@@\n-a\n+b\n*** End Patch"})
            result = subprocess.run(command, shell=True, cwd=self.cwd, input=json.dumps(event),
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {})


class InstallTests(unittest.TestCase):
    def test_install_is_idempotent_and_does_not_enable_hooks(self):
        with tempfile.TemporaryDirectory() as temporary:
            command = [sys.executable, str(ROOT / "scripts/install_factory.py"), "--codex-home", temporary]
            for _ in range(2):
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((Path(temporary) / "skills/software-factory").resolve(), ROOT / "skills/software-factory")
            self.assertFalse((Path(temporary) / "hooks.json").exists())

    def test_installer_preserves_existing_skill_and_dangling_links(self):
        for dangling in (False, True):
            with self.subTest(dangling=dangling), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / "skills/software-factory"
                target.parent.mkdir()
                if dangling:
                    target.symlink_to(Path(temporary) / "missing")
                else:
                    target.mkdir()
                    (target / "SKILL.md").write_text("existing")
                result = subprocess.run([sys.executable, str(ROOT / "scripts/install_factory.py"),
                                         "--codex-home", temporary], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn("preserved", result.stderr)
                self.assertTrue(target.is_symlink() if dangling else (target / "SKILL.md").read_text() == "existing")


if __name__ == "__main__":
    unittest.main()
