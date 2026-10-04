#!/usr/bin/env python3
"""Create a metadata-only index for each completed Harbor trial."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED = {
    "agent/trajectory.json",
    "agent/terminus_2.pane",
    "agent/recording.cast",
    "agent/terminal.cast",
    "result.json",
    "trial.log",
    "exception.txt",
    "artifacts/manifest.json",
    "verifier/reward.txt",
    "verifier/test-stdout.txt",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def index_trial(trial: Path) -> None:
    files = []
    for path in sorted(p for p in trial.rglob("*") if p.is_file()):
        if path.name == "trace-index.json":
            continue
        files.append(
            {
                "path": path.relative_to(trial).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": digest(path),
            }
        )
    present = {item["path"] for item in files}
    payload = {
        "schema_version": "trace-index-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "expected_trace_files": sorted(EXPECTED),
        "present_expected_trace_files": sorted(EXPECTED & present),
        "missing_expected_trace_files": sorted(EXPECTED - present),
    }
    (trial / "trace-index.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} TRIALS_DIR", file=sys.stderr)
        return 2
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"trial directory does not exist: {root}", file=sys.stderr)
        return 2
    trials = sorted(p.parent for p in root.glob("*/result.json"))
    for trial in trials:
        index_trial(trial)
        print(f"indexed: {trial}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
