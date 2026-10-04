#!/usr/bin/env python3
"""Render descriptive figures from the published seven-minute replicate traces."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
TRACE_ROOT = ROOT / "traces" / "local-gpt-6-sol"
OUTPUT = ROOT / "renders"

GROUPS = (
    (
        "06_replicates_10x/embedded_answer_host_tools",
        "Answer artifact · host-tool lane",
    ),
    ("06_replicates_10x/embedded_url_host_tools", "URL artifact · host-tool lane"),
    ("06_replicates_10x/embedded_url_public", "URL artifact · public container"),
    ("06_replicates_10x/no_artifact_host_tools", "Clean control · host-tool lane"),
    ("06_replicates_10x/no_artifact_public", "Clean control · public container"),
    (
        "07_explicit_frontier_benchmark/explicit_frontier_url_public",
        "FrontierMath named · URL · public",
    ),
    (
        "08_explicit_frontier_source_cue/explicit_frontier_url_public_source_cue",
        "Source cue · URL · public",
    ),
)
LABELS = dict(GROUPS)

NAVY = "#20324a"
TEAL = "#087f8c"
ORANGE = "#d58420"
RED = "#b54f45"
GRAY = "#8f9aa5"
PALE = "#e7edf1"


@dataclass(frozen=True)
class Trial:
    group: str
    replicate: int
    reward: float | None
    timeout: bool
    infrastructure_failure: bool


def read_trials() -> dict[str, list[Trial]]:
    groups: dict[str, list[Trial]] = {group: [] for group, _ in GROUPS}
    for path in TRACE_ROOT.rglob("metadata.json"):
        data = json.loads(path.read_text())
        group = data["archive_condition"]
        if group not in groups:
            continue
        exception = data.get("exception") or {}
        trial = Trial(
            group=group,
            replicate=int(data["trace_run"].split("-")[-1]),
            reward=data.get("reward"),
            timeout=exception.get("type") == "AgentTimeoutError",
            infrastructure_failure=exception.get("type") == "RuntimeError",
        )
        groups[group].append(trial)
    for group, trials in groups.items():
        trials.sort(key=lambda trial: trial.replicate)
        if not trials:
            raise ValueError(f"No published trials for {group}")
        if len({trial.replicate for trial in trials}) != len(trials):
            raise ValueError(f"Duplicate replicate in {group}")
        if any(trial.reward not in (0, 0.0, 1, 1.0, None) for trial in trials):
            raise ValueError(f"Unexpected reward in {group}")
        if any(
            trial.infrastructure_failure and trial.reward is not None
            for trial in trials
        ):
            raise ValueError(f"Infrastructure failure with reward in {group}")
    return groups


def scored(trials: list[Trial]) -> tuple[int, int]:
    eligible = [trial for trial in trials if not trial.infrastructure_failure]
    return sum(trial.reward == 1 for trial in eligible), len(eligible)


def wilson(
    successes: int, total: int, z: float = 1.959963984540054
) -> tuple[float, float]:
    """Two-sided 95% Wilson score interval for a Bernoulli proportion."""
    if total == 0:
        raise ValueError("Cannot estimate a pass rate with no scored trials")
    p = successes / total
    z2 = z * z
    center = (p + z2 / (2 * total)) / (1 + z2 / total)
    radius = (
        z * math.sqrt(p * (1 - p) / total + z2 / (4 * total * total)) / (1 + z2 / total)
    )
    return max(0.0, center - radius), min(1.0, center + radius)


def newcombe(a: tuple[int, int], b: tuple[int, int]) -> tuple[float, float]:
    """95% Newcombe hybrid-score interval for two independent proportions."""
    k1, n1 = a
    k0, n0 = b
    p1, p0 = k1 / n1, k0 / n0
    l1, u1 = wilson(k1, n1)
    l0, u0 = wilson(k0, n0)
    lower = p1 - p0 - math.hypot(p1 - l1, u0 - p0)
    upper = p1 - p0 + math.hypot(u1 - p1, p0 - l0)
    return max(-1.0, lower), min(1.0, upper)


def finish(fig: plt.Figure, stem: str) -> None:
    OUTPUT.mkdir(exist_ok=True)
    for suffix in ("svg", "png"):
        path = OUTPUT / f"{stem}.{suffix}"
        fig.savefig(
            path,
            dpi=210,
            facecolor="white",
            metadata={"Date": None} if suffix == "svg" else None,
        )
        if suffix == "svg":
            path.write_text(
                "\n".join(line.rstrip() for line in path.read_text().splitlines())
                + "\n"
            )
    plt.close(fig)


def forest(groups: dict[str, list[Trial]]) -> None:
    fig, ax = plt.subplots(figsize=(11.4, 6.4))
    fig.set_facecolor("white")
    fig.subplots_adjust(left=0.36, right=0.90, bottom=0.21, top=0.87)
    ax.set_facecolor("white")
    ax.axvspan(0, 1, color="#f7f9fa", zorder=0)
    ax.axhline(2.5, color=PALE, linewidth=1.4)
    for index, (key, label) in enumerate(GROUPS):
        y = len(GROUPS) - 1 - index
        k, n = scored(groups[key])
        p = k / n
        lo, hi = wilson(k, n)
        color = TEAL if index < 5 else ORANGE
        ax.plot([lo, hi], [y, y], color=color, linewidth=3, solid_capstyle="round")
        ax.plot([lo, lo], [y - 0.12, y + 0.12], color=color, linewidth=1.6)
        ax.plot([hi, hi], [y - 0.12, y + 0.12], color=color, linewidth=1.6)
        ax.scatter(p, y, s=112, color=color, edgecolors="white", linewidths=1, zorder=3)
        ax.text(1.035, y, f"{k}/{n}  ({p:.0%})", va="center", color=NAVY, fontsize=11)
    ax.set_yticks(range(len(GROUPS)), [LABELS[key] for key, _ in GROUPS[::-1]])
    ax.set_xlim(-0.02, 1.22)
    ax.set_ylim(-0.65, len(GROUPS) - 0.35)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("Verifier pass rate · 95% Wilson interval", color=NAVY, labelpad=10)
    ax.set_title(
        "Verifier pass rates across seven-minute replicate conditions",
        loc="left",
        color=NAVY,
        weight="bold",
        pad=18,
    )
    ax.grid(axis="x", color=PALE, linewidth=1)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10, labelcolor=NAVY)
    ax.tick_params(axis="x", colors=NAVY)
    fig.text(
        0.36,
        0.075,
        "Local GPT-6-sol trials · reward=1 counts as pass, even when a timeout was recorded.",
        color="#526171",
        fontsize=9,
    )
    fig.text(
        0.36,
        0.045,
        "Clean public control: 1 setup failure excluded (2/4 scored). Intervals are descriptive.",
        color="#526171",
        fontsize=9,
    )
    finish(fig, "pass-rate-forest")


def outcome_grid(groups: dict[str, list[Trial]]) -> None:
    fig, ax = plt.subplots(figsize=(11.4, 6.1), layout="constrained")
    fig.set_facecolor("white")
    ax.set_facecolor("white")
    for index, (key, _) in enumerate(GROUPS):
        y = len(GROUPS) - 1 - index
        for trial in groups[key]:
            x = trial.replicate
            if trial.infrastructure_failure:
                ax.scatter(x, y, marker="x", color=GRAY, s=96, linewidths=2.3, zorder=3)
            elif trial.reward == 1 and trial.timeout:
                ax.scatter(
                    x,
                    y,
                    marker="D",
                    color=TEAL,
                    s=75,
                    edgecolors="white",
                    linewidths=1,
                    zorder=3,
                )
            elif trial.reward == 1:
                ax.scatter(
                    x,
                    y,
                    marker="o",
                    color=TEAL,
                    s=93,
                    edgecolors="white",
                    linewidths=1,
                    zorder=3,
                )
            elif trial.timeout:
                ax.scatter(
                    x,
                    y,
                    marker="s",
                    color=ORANGE,
                    s=82,
                    edgecolors="white",
                    linewidths=1,
                    zorder=3,
                )
            else:
                ax.scatter(
                    x,
                    y,
                    marker="o",
                    facecolors="white",
                    edgecolors=RED,
                    s=93,
                    linewidths=2,
                    zorder=3,
                )
    ax.axhline(2.5, color=PALE, linewidth=1.4)
    ax.set_yticks(range(len(GROUPS)), [LABELS[key] for key, _ in GROUPS[::-1]])
    ax.set_xticks(range(1, 11))
    ax.set_xlim(0.3, 10.7)
    ax.set_ylim(-0.6, len(GROUPS) - 0.4)
    ax.set_xlabel("Replicate number", color=NAVY, labelpad=10)
    ax.set_title(
        "Every recorded trial, including timeouts and setup failure",
        loc="left",
        color=NAVY,
        weight="bold",
        pad=18,
    )
    ax.grid(axis="x", color=PALE, linewidth=1)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10, labelcolor=NAVY)
    ax.tick_params(axis="x", colors=NAVY)
    legend = [
        Line2D(
            [], [], marker="o", linestyle="", color=TEAL, markersize=9, label="Pass"
        ),
        Line2D(
            [],
            [],
            marker="D",
            linestyle="",
            color=TEAL,
            markersize=8,
            label="Pass + timeout",
        ),
        Line2D(
            [],
            [],
            marker="o",
            linestyle="",
            markerfacecolor="white",
            markeredgecolor=RED,
            markeredgewidth=1.7,
            markersize=9,
            label="Fail",
        ),
        Line2D(
            [],
            [],
            marker="s",
            linestyle="",
            color=ORANGE,
            markersize=8,
            label="Fail + timeout",
        ),
        Line2D(
            [],
            [],
            marker="x",
            linestyle="",
            color=GRAY,
            markeredgewidth=2,
            markersize=9,
            label="Setup failure",
        ),
    ]
    ax.legend(
        handles=legend,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.13),
        ncol=5,
        frameon=False,
        fontsize=9,
    )
    finish(fig, "trial-outcomes")


def contrasts(groups: dict[str, list[Trial]]) -> None:
    comparisons = (
        ("Answer artifact vs clean · host-tool lane", GROUPS[0][0], GROUPS[3][0]),
        ("URL artifact vs clean · host-tool lane", GROUPS[1][0], GROUPS[3][0]),
        ("URL artifact vs clean · public container", GROUPS[2][0], GROUPS[4][0]),
        ("FrontierMath named vs URL · public", GROUPS[5][0], GROUPS[2][0]),
        ("Source cue vs FrontierMath named · public", GROUPS[6][0], GROUPS[5][0]),
    )
    fig, ax = plt.subplots(figsize=(11.4, 5.2))
    fig.set_facecolor("white")
    fig.subplots_adjust(left=0.40, right=0.90, bottom=0.22, top=0.86)
    ax.set_facecolor("white")
    ax.axvspan(-1, 1, color="#f7f9fa", zorder=0)
    ax.axvline(0, color=GRAY, linewidth=1.3, linestyle="--")
    for index, (label, target, reference) in enumerate(comparisons):
        y = len(comparisons) - 1 - index
        a, b = scored(groups[target]), scored(groups[reference])
        delta = a[0] / a[1] - b[0] / b[1]
        lo, hi = newcombe(a, b)
        color = TEAL if index < 3 else ORANGE
        ax.plot([lo, hi], [y, y], color=color, linewidth=3, solid_capstyle="round")
        ax.plot([lo, lo], [y - 0.12, y + 0.12], color=color, linewidth=1.6)
        ax.plot([hi, hi], [y - 0.12, y + 0.12], color=color, linewidth=1.6)
        ax.scatter(
            delta, y, color=color, s=112, edgecolors="white", linewidths=1, zorder=3
        )
        ax.text(1.04, y, f"{delta:+.0%}", color=NAVY, va="center", fontsize=11)
    ax.set_yticks(range(len(comparisons)), [label for label, _, _ in comparisons[::-1]])
    ax.set_xlim(-1.03, 1.18)
    ax.set_ylim(-0.65, len(comparisons) - 0.35)
    ax.set_xticks([-1, -0.5, 0, 0.5, 1], ["−100", "−50", "0", "+50", "+100"])
    ax.set_xlabel(
        "Difference in verifier pass rate (percentage points) · 95% Newcombe interval",
        color=NAVY,
        labelpad=10,
    )
    ax.set_title(
        "Exploratory differences between selected conditions",
        loc="left",
        color=NAVY,
        weight="bold",
        pad=18,
    )
    ax.grid(axis="x", color=PALE, linewidth=1)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10, labelcolor=NAVY)
    ax.tick_params(axis="x", colors=NAVY)
    fig.text(
        0.40,
        0.075,
        "Intervals are descriptive; these small trials were not a randomized causal study.",
        color="#526171",
        fontsize=9,
    )
    finish(fig, "condition-contrasts")


def main() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "svg.fonttype": "none",
            "svg.hashsalt": "bmo-optimization-agent-behavior",
        }
    )
    groups = read_trials()
    forest(groups)
    outcome_grid(groups)
    contrasts(groups)
    for key, _ in GROUPS:
        k, n = scored(groups[key])
        print(f"{key}: {k}/{n}")
    print(f"Wrote figures to {OUTPUT}")


if __name__ == "__main__":
    main()
