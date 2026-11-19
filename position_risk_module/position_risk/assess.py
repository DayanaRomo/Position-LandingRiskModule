"""Core analysis: per-point error statistics, plan checks, and the R2 risk verdict."""
import math
import operator
from dataclasses import dataclass, field
from typing import List

import numpy as np

from .config import Criteria, RISK
from .data import Readings

_OPS = {"<=": operator.le, ">=": operator.ge}
TOL = 1e-9   # absorbs floating-point noise so a reading of exactly 10.000 cm is not called 10.0000000001 cm


def wilson_upper(k: int, n: int, confidence: float = 0.95) -> float:
    """Upper confidence bound on the true exceedance probability given k exceedances in n readings.
    With k = 0 this is close to the 'rule of three' (about 3 / n)."""
    if n <= 0:
        return 1.0
    z = {0.90: 1.2816, 0.95: 1.6449, 0.99: 2.3263}.get(confidence, 1.6449)   # one-sided
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return min(1.0, (centre + half) / denom)


@dataclass
class PointStat:
    point: int
    x_m: float
    y_m: float
    n: int
    mean_err_m: float
    p95_err_m: float
    worst_err_m: float
    bias_x_m: float
    bias_y_m: float
    passed: bool


@dataclass
class Check:
    name: str
    value: float
    op: str
    limit: float
    unit: str
    source: str
    passed: bool = False

    def evaluate(self):
        slack = TOL if self.op == "<=" else -TOL
        self.passed = bool(self.value == self.value and _OPS[self.op](self.value, self.limit + slack))
        return self


@dataclass
class Assessment:
    label: str
    source: str
    criteria: Criteria
    points: List[PointStat]
    errors: np.ndarray
    checks: List[Check]
    warnings: List[str] = field(default_factory=list)
    n_readings: int = 0
    mean_err_m: float = 0.0
    median_err_m: float = 0.0
    p95_err_m: float = 0.0
    worst_err_m: float = 0.0
    n_exceed: int = 0
    exceed_frac: float = 0.0
    exceed_upper: float = 0.0
    overall_bias_m: tuple = (0.0, 0.0)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def warning_signal_tripped(self) -> bool:
        # The plan's warning signal: bench position error above the limit.
        return self.worst_err_m > self.criteria.limit_m + TOL

    @property
    def failing_points(self):
        return [p for p in self.points if not p.passed]

    @property
    def margin_pct(self) -> float:
        """Headroom below the limit as a share of the limit (negative = over the limit)."""
        return (self.criteria.limit_m - self.worst_err_m) / self.criteria.limit_m * 100


def assess(r: Readings, crit: Criteria = Criteria()) -> Assessment:
    err_vec = r.meas - r.true
    err = np.linalg.norm(err_vec, axis=1)
    points, warnings = [], []
    for pid in sorted(set(r.point.tolist())):
        m = r.point == pid
        e = err[m]
        t = r.true[m].mean(axis=0)
        bv = err_vec[m].mean(axis=0)
        points.append(PointStat(int(pid), float(t[0]), float(t[1]), int(m.sum()), float(e.mean()),
                                float(np.percentile(e, 95)), float(e.max()), float(bv[0]), float(bv[1]),
                                bool(e.max() <= crit.limit_m + TOL)))
    counts = [p.n for p in points]
    checks = [
        Check("Worst-case error at every grid point", max(p.worst_err_m for p in points), "<=", crit.limit_m, "m", "slide").evaluate(),
        Check("Readings at the least-sampled point", min(counts), ">=", crit.min_readings, "readings", "slide").evaluate(),
        Check("Grid points tested", len(points), ">=", crit.min_points, "points", "default").evaluate(),
    ]
    xs = sorted({round(p.x_m, 4) for p in points})
    ys = sorted({round(p.y_m, 4) for p in points})
    steps = [b - a for s in (xs, ys) for a, b in zip(s, s[1:])]
    if steps and abs(min(steps) - crit.grid_spacing_m) > 0.05 * crit.grid_spacing_m:
        warnings.append(f"Smallest grid spacing is {min(steps):.3f} m, but the plan specifies {crit.grid_spacing_m} m.")
    if len(set(counts)) > 1:
        warnings.append("Points have different numbers of readings: " + ", ".join(f"{c}" for c in sorted(set(counts))) + ".")
    if r.source == "simulated":
        warnings.append("SIMULATED DATA: these results test the software and do not count as the bench test.")
    n_exceed = int((err > crit.limit_m + TOL).sum())
    a = Assessment(
        label=r.label, source=r.source, criteria=crit, points=points, errors=err, checks=checks, warnings=warnings,
        n_readings=len(err), mean_err_m=float(err.mean()), median_err_m=float(np.median(err)),
        p95_err_m=float(np.percentile(err, 95)), worst_err_m=float(err.max()), n_exceed=n_exceed,
        exceed_frac=n_exceed / len(err), exceed_upper=wilson_upper(n_exceed, len(err), crit.confidence),
        overall_bias_m=(float(err_vec[:, 0].mean()), float(err_vec[:, 1].mean())),
    )
    return a


def risk_status(a: Assessment) -> dict:
    """What the result means for risk R2 in the plan."""
    simulated = a.source == "simulated"
    if a.passed:
        status = "Warning signal clear" + (" (simulated)" if simulated else "")
        action = ("Keep this sensor setup. Repeat the test on the real sensor and bench grid." if simulated
                  else "R2 is reduced for this setup. Repeat if the sensor, lighting, or mounting changes.")
    else:
        status = "WARNING SIGNAL TRIPPED" + (" (simulated)" if simulated else "")
        action = RISK["if_fails"] + ". Tell the team immediately (plan slide 3)."
    return {"risk": f"{RISK['id']} {RISK['name']}", "chance": RISK["chance"], "impact": RISK["impact"],
            "owner": RISK["owner"], "status": status, "action": action}
