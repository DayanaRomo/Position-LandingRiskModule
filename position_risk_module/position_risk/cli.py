"""Command line: python -m position_risk"""
import argparse
import os
import sys
from datetime import datetime

from . import __version__
from .assess import assess, risk_status
from .config import Criteria
from .data import load_csv, write_template
from .report import write_outputs
from .sim import SCENARIOS, simulate


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m position_risk",
                                 description="R2 indoor position error risk assessment (simulated by default).")
    ap.add_argument("--csv", help="real bench-test data (columns: point,x_true_m,y_true_m,x_meas_m,y_meas_m)")
    ap.add_argument("--units", default="m", choices=["m", "cm", "mm"], help="units used in the CSV (default m)")
    ap.add_argument("--scenario", choices=list(SCENARIOS) + ["all"], default="all", help="simulated setup (default all)")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--readings", type=int, help="readings per point for simulation (default 20)")
    ap.add_argument("--out", help="output folder (default: risk_results/<timestamp>)")
    ap.add_argument("--no-plots", action="store_true")
    ap.add_argument("--list-scenarios", action="store_true")
    ap.add_argument("--make-template", metavar="FILE", help="write a blank bench-test CSV and exit")
    a = ap.parse_args(argv)
    if a.list_scenarios:
        for s in SCENARIOS.values():
            print(f"{s.name:14s} {s.description}")
        return 0
    if a.make_template:
        write_template(a.make_template)
        print(f"Template written to {a.make_template}")
        return 0
    crit = Criteria()
    items = []
    try:
        if a.csv:
            r = load_csv(a.csv, a.units, label=os.path.splitext(os.path.basename(a.csv))[0])
            items.append((assess(r, crit), r))
        else:
            names = list(SCENARIOS) if a.scenario == "all" else [a.scenario]
            for n in names:
                r = simulate(n, a.seed, crit, readings_per_point=a.readings)
                items.append((assess(r, crit), r))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    out = a.out or os.path.join("risk_results", datetime.now().strftime("%Y%m%d_%H%M%S"))
    path = write_outputs(out, items, make_plots=not a.no_plots, version=__version__)
    for asmt, _ in items:
        print(f"[{'PASS' if asmt.passed else 'FAIL'}] {asmt.label}: worst {asmt.worst_err_m * 100:.1f} cm, "
              f"mean {asmt.mean_err_m * 100:.1f} cm, limit {crit.limit_m * 100:.0f} cm | {risk_status(asmt)['status']}")
    print(f"\nReport: {os.path.abspath(path)}")
    if len(items) > 1:
        return 0   # comparison runs are informational
    return 0 if items[0][0].passed else 1


if __name__ == "__main__":
    sys.exit(main())
