"""Self-contained, safe HTML projection of a board snapshot."""

import base64
import json
from pathlib import Path

from .state import atomic_write, validate_snapshot


def render(snapshot):
    validate_snapshot(snapshot)
    template = Path(__file__).with_name("board.html").read_text(encoding="utf-8")
    # Base64 prevents issue text from closing a script tag or becoming executable markup.
    data = base64.b64encode(json.dumps(snapshot, ensure_ascii=False).encode("utf-8")).decode("ascii")
    return template.replace("__FACTORY_DATA__", data)


def write_board(snapshot, path):
    atomic_write(path, render(snapshot))
