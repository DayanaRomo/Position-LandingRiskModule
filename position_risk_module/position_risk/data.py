"""Reading data: CSV loading, validation, and a template for real bench tests."""
import csv
from dataclasses import dataclass

import numpy as np

COLUMNS = ["point", "x_true_m", "y_true_m", "x_meas_m", "y_meas_m"]
_UNITS = {"m": 1.0, "cm": 0.01, "mm": 0.001}


@dataclass
class Readings:
    label: str
    point: np.ndarray    # [N] integer point ids
    true: np.ndarray     # [N,2] tape-measured position, metres
    meas: np.ndarray     # [N,2] sensor reading, metres
    source: str = "simulated"

    def __post_init__(self):
        if not (len(self.point) == len(self.true) == len(self.meas)):
            raise ValueError("point, true, and meas must have the same length")
        if len(self.point) == 0:
            raise ValueError("no readings")
        if not (np.isfinite(self.true).all() and np.isfinite(self.meas).all()):
            raise ValueError("readings contain NaN or infinite values")


def load_csv(path: str, units: str = "m", label: str = None) -> Readings:
    if units not in _UNITS:
        raise ValueError(f"units must be one of {list(_UNITS)}")
    k = _UNITS[units]
    with open(path, newline="") as f:
        rd = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (rd.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV is missing columns: {missing}. Expected: {COLUMNS}")
        rows = [r for r in rd if any((v or "").strip() for v in r.values())]
    if not rows:
        raise ValueError("CSV has no data rows")
    try:
        pts = np.array([int(float(r["point"])) for r in rows])
        true = np.array([[float(r["x_true_m"]), float(r["y_true_m"])] for r in rows]) * k
        meas = np.array([[float(r["x_meas_m"]), float(r["y_meas_m"])] for r in rows]) * k
    except ValueError as e:
        raise ValueError(f"CSV contains a non-numeric value: {e}")
    return Readings(label or path, pts, true, meas, source="csv")


def write_csv(path: str, r: Readings):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for p, t, m in zip(r.point, r.true, r.meas):
            w.writerow([int(p), f"{t[0]:.5f}", f"{t[1]:.5f}", f"{m[0]:.5f}", f"{m[1]:.5f}"])


def write_template(path: str):
    """Blank bench-test sheet: one row per reading. Values below are examples only; delete them."""
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        w.writerow([1, "0.000", "0.000", "0.012", "-0.008"])
        w.writerow([1, "0.000", "0.000", "0.009", "-0.011"])
        w.writerow([2, "0.500", "0.000", "0.511", "0.004"])
