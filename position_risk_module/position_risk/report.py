"""Writes the risk assessment report, CSV data, and plots."""
import csv
import json
import os
from datetime import datetime, timezone
from typing import List

import numpy as np

from .assess import Assessment, risk_status
from .config import RISK
from .data import Readings, write_csv


def _cm(x):
    return f"{x * 100:.1f}"


def write_outputs(out_dir: str, items: List[tuple], make_plots: bool = True, version: str = "1.0.0") -> str:
    """items: list of (Assessment, Readings). Returns path of the markdown report."""
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    any_sim = any(a.source == "simulated" for a, _ in items)
    L = ["# R2 Indoor Position Error: Risk Assessment\n"]
    if any_sim:
        L.append("> **SIMULATED DATA.** The numbers below come from a software model of the sensors. They test this tool and the "
                 "plan's decision logic. They do not count as the bench test and say nothing about real hardware.\n")
    L.append(f"- Risk: **{RISK['id']} {RISK['name']}** (chance {RISK['chance']}, impact {RISK['impact']}, owner {RISK['owner']})")
    L.append(f"- Plan response: {RISK['response']}")
    L.append(f"- Warning signal: {RISK['warning_signal']}")
    L.append(f"- Pass criterion: error at most {_cm(items[0][0].criteria.limit_m)} cm at every grid point, "
             f"at least {items[0][0].criteria.min_readings} readings per point, tape-measured truth")
    L.append(f"- Generated (UTC): {stamp}  |  Module version {version}\n")
    if len(items) > 1:
        L.append("## Comparison\n")
        L.append("| Setup | Worst error (cm) | Mean error (cm) | Points over limit | Readings over limit | 95% upper bound on exceedance | Result |")
        L.append("|---|---|---|---|---|---|---|")
        for a, _ in items:
            L.append(f"| {a.label} | {_cm(a.worst_err_m)} | {_cm(a.mean_err_m)} | {len(a.failing_points)} of {len(a.points)} | "
                     f"{a.n_exceed} of {a.n_readings} | {a.exceed_upper * 100:.1f}% | {'PASS' if a.passed else '**FAIL**'} |")
        L.append("")
    for a, r in items:
        rs = risk_status(a)
        L.append(f"## {a.label}: {'PASS' if a.passed else 'FAIL'}\n")
        L.append(f"**Risk status:** {rs['status']}. {rs['action']}\n")
        L.append("| Check | Measured | Limit | Basis | Result |")
        L.append("|---|---|---|---|---|")
        for c in a.checks:
            v = _cm(c.value) + " cm" if c.unit == "m" else f"{c.value:g} {c.unit}"
            lim = _cm(c.limit) + " cm" if c.unit == "m" else f"{c.limit:g} {c.unit}"
            L.append(f"| {c.name} | {v} | {c.op} {lim} | {'Slide' if c.source == 'slide' else 'Default (confirm)'} | {'PASS' if c.passed else '**FAIL**'} |")
        L.append("")
        L.append(f"- Readings: {a.n_readings} at {len(a.points)} points. Mean error {_cm(a.mean_err_m)} cm, median {_cm(a.median_err_m)} cm, "
                 f"95th percentile {_cm(a.p95_err_m)} cm, worst {_cm(a.worst_err_m)} cm.")
        L.append(f"- Headroom: worst case is {abs(a.margin_pct):.0f}% {'below' if a.margin_pct >= 0 else 'above'} the limit.")
        L.append(f"- Overall bias (reading minus truth): x {_cm(a.overall_bias_m[0])} cm, y {_cm(a.overall_bias_m[1])} cm.")
        L.append(f"- {a.n_exceed} of {a.n_readings} readings exceeded the limit. With {int(a.criteria.confidence * 100)}% confidence, "
                 f"at most {a.exceed_upper * 100:.1f}% of readings from this setup exceed it (assumes independent readings).")
        if a.failing_points:
            worst = sorted(a.failing_points, key=lambda p: -p.worst_err_m)[:5]
            L.append("- Failing points (worst five): " + "; ".join(
                f"point {p.point} at ({p.x_m:.1f}, {p.y_m:.1f}) m, worst {_cm(p.worst_err_m)} cm" for p in worst))
        for w in a.warnings:
            L.append(f"- Note: {w}")
        L.append("")
    L.append("## Limits of this assessment\n")
    L.append("- Worst case over a few hundred readings is not a guarantee; rare bad detections can still occur in flight.")
    L.append("- The exceedance bound assumes independent readings. Readings taken at one static point share the same bias, so treat it as optimistic.")
    L.append("- Error is measured against a tape-measured position, which itself has a few millimetres of uncertainty.")
    L.append("- Bench error on a cart is not flight error: vibration, motion blur, and downwash are not tested here.")
    path = os.path.join(out_dir, "risk_assessment.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")

    summary = []
    for a, r in items:
        slug = a.label.lower().replace(" ", "_")
        write_csv(os.path.join(out_dir, f"{slug}_readings.csv"), r)
        with open(os.path.join(out_dir, f"{slug}_points.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["point", "x_m", "y_m", "n", "mean_err_m", "p95_err_m", "worst_err_m", "bias_x_m", "bias_y_m", "passed"])
            for p in a.points:
                w.writerow([p.point, p.x_m, p.y_m, p.n, f"{p.mean_err_m:.5f}", f"{p.p95_err_m:.5f}", f"{p.worst_err_m:.5f}",
                            f"{p.bias_x_m:.5f}", f"{p.bias_y_m:.5f}", int(p.passed)])
        summary.append({"label": a.label, "source": a.source, "passed": a.passed, "risk_status": risk_status(a),
                        "worst_err_m": a.worst_err_m, "mean_err_m": a.mean_err_m, "p95_err_m": a.p95_err_m,
                        "n_readings": a.n_readings, "n_points": len(a.points), "n_exceed": a.n_exceed,
                        "exceed_upper_95": a.exceed_upper, "failing_points": [p.point for p in a.failing_points],
                        "checks": [{"name": c.name, "value": c.value, "op": c.op, "limit": c.limit, "passed": c.passed} for c in a.checks]})
    with open(os.path.join(out_dir, "risk_assessment.json"), "w") as f:
        json.dump({"generated_utc": stamp, "risk": RISK, "assessments": summary}, f, indent=2)
    if make_plots:
        _plots(out_dir, items)
    return path


def _plots(out_dir, items):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    lim = items[0][0].criteria.limit_m * 100
    for a, _ in items:
        fig, ax = plt.subplots(figsize=(5.2, 4.6))
        xs = [p.x_m for p in a.points]; ys = [p.y_m for p in a.points]; ws = [p.worst_err_m * 100 for p in a.points]
        sc = ax.scatter(xs, ys, c=ws, s=900, cmap="RdYlGn_r", vmin=0, vmax=max(lim * 1.5, max(ws)), edgecolors=["red" if w > lim else "black" for w in ws], linewidths=2)
        for x, y, w in zip(xs, ys, ws):
            ax.text(x, y, f"{w:.1f}", ha="center", va="center", fontsize=8)
        ax.margins(0.18); ax.set_aspect("equal"); ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
        ax.set_title(f"{a.label}: worst error per point (cm)\nred outline = over {lim:.0f} cm limit", fontsize=10)
        fig.colorbar(sc, ax=ax, label="cm"); fig.tight_layout()
        fig.savefig(os.path.join(out_dir, f"plot_map_{a.label.lower().replace(' ', '_')}.png"), dpi=110); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.4, 4))
    for a, _ in items:
        ax.hist(a.errors * 100, bins=40, alpha=0.55, label=f"{a.label} (worst {a.worst_err_m * 100:.1f} cm)")
    ax.axvline(lim, color="red", ls="--", label=f"Limit {lim:.0f} cm")
    ax.set_xlabel("Position error (cm)"); ax.set_ylabel("Readings"); ax.set_title("Position error distribution"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(out_dir, "plot_error_distribution.png"), dpi=110); plt.close(fig)
