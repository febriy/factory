"""Versioned snapshots and one-writer file storage."""

import contextlib
import fcntl
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone


class FactoryError(Exception):
    """A user-actionable factory failure."""


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def validate_snapshot(data):
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise FactoryError("Unsupported board snapshot. Expected schema_version 1.")
    if data.get("source") not in ("github", "demo"):
        raise FactoryError("Snapshot has an invalid source.")
    if not isinstance(data.get("issues"), list):
        raise FactoryError("Snapshot issues must be a list.")
    if not isinstance(data.get("sync"), dict):
        raise FactoryError("Snapshot is missing its synchronization record.")
    if data["sync"].get("status") not in ("demo", "fresh", "partial", "error"):
        raise FactoryError("Snapshot has an invalid synchronization status.")
    if data["source"] == "github" and not isinstance(data.get("repository"), str):
        raise FactoryError("GitHub snapshot has no repository binding.")
    if not isinstance(data.get("scope"), dict) or not isinstance(data.get("generated_at"), str):
        raise FactoryError("Snapshot is missing its scope or generation time.")
    ids = set()
    for issue in data["issues"]:
        if not isinstance(issue, dict) or not isinstance(issue.get("id"), str):
            raise FactoryError("Snapshot contains an invalid issue.")
        if issue["id"] in ids:
            raise FactoryError("Snapshot contains duplicate issue IDs.")
        ids.add(issue["id"])
        if not isinstance(issue.get("title"), str):
            raise FactoryError("Snapshot contains an issue with no title.")
        if issue.get("status") not in ("triage", "planned", "ready", "running", "review", "done", "blocked", "cancelled"):
            raise FactoryError("Snapshot contains an invalid workflow status.")
        if issue.get("state") not in ("open", "closed") or not isinstance(issue.get("body"), str):
            raise FactoryError("Snapshot contains an invalid issue state or description.")
        if not isinstance(issue.get("number"), int) or issue["number"] < 1:
            raise FactoryError("Snapshot contains an invalid issue number.")
        for field in ("labels", "assignees", "warnings", "blockers"):
            if not isinstance(issue.get(field), list):
                raise FactoryError("Snapshot contains an invalid issue field: " + field)
    return data


def atomic_write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Store:
    def __init__(self, directory):
        self.directory = Path(directory).expanduser().resolve()

    @contextlib.contextmanager
    def lock(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / ".lock").open("a", encoding="utf-8") as stream:
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise FactoryError("Another factory command is updating this board. Try again when it finishes.")
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def load(self):
        path = self.directory / "board.json"
        if not path.exists():
            return None
        try:
            return validate_snapshot(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            raise FactoryError("Cannot read board.json. The existing snapshot has been preserved.") from exc

    def save(self, data):
        validate_snapshot(data)
        atomic_write(self.directory / "board.json", json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    def event(self, kind, **details):
        # This is an audit trail, not a transaction log or a worker claim.
        record = {"at": utc_now(), "kind": kind, **details}
        with (self.directory / "events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
