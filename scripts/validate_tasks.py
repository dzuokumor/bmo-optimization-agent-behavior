"""Validate task fixtures without starting model trials."""

from __future__ import annotations

from pathlib import Path
import importlib
import tomllib

ROOT = Path(__file__).resolve().parents[1]
TASK_ROOT = ROOT / "experiments" / "frontiermath" / "bmo-optimization"
REQUIRED = (
    "instruction.md",
    "task.toml",
    "environment/Dockerfile",
    "environment/problem.tex",
    "environment/entrypoint.sh",
    "environment/time_remaining",
    "solution/solve.sh",
    "tests/test.sh",
)


def main() -> None:
    harbor_config = None
    try:
        harbor_config = importlib.import_module("harbor.models.task.config").TaskConfig
    except (ImportError, ModuleNotFoundError):
        pass

    count = 0
    for task_dir in sorted(TASK_ROOT.iterdir()):
        if not task_dir.is_dir():
            continue
        data = tomllib.loads((task_dir / "task.toml").read_text(encoding="utf-8"))
        expected_network = data["environment"]["network_mode"]
        assert data["agent"]["network_mode"] == expected_network
        assert data["verifier"]["network_mode"] == "no-network"
        for required in REQUIRED:
            assert (task_dir / required).is_file(), f"{task_dir}: missing {required}"
        if harbor_config is not None:
            task = harbor_config.model_validate_toml(
                (task_dir / "task.toml").read_text(encoding="utf-8")
            )
            assert task.task.name
        print(f"valid: {data['task']['name']}")
        count += 1
    print(f"validated {count} task fixtures")


if __name__ == "__main__":
    main()
