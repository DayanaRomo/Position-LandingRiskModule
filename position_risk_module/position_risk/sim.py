"""Simulated position sensors for the three setups the plan cares about.

All parameters are ASSUMPTIONS chosen to be plausible for a camera-based indoor sensor.
They are not measurements. Replace the simulation with a real bench test (--csv)."""
import math
from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np

from .config import Criteria
from .data import Readings


@dataclass(frozen=True)
class SensorModel:
    bias_m: Tuple[float, float]
    scale: float
    rot_deg: float
    noise_m: float            # per-axis Gaussian noise
    outlier_prob: float       # chance a reading is a bad detection
    outlier_sd_m: float       # extra per-axis error on a bad detection


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    sensors: Tuple[SensorModel, ...] = field(default_factory=tuple)


SCENARIOS = {
    "baseline": Scenario(
        "baseline", "Camera only, no markers (the setup before any mitigation)",
        (SensorModel((0.035, -0.025), 1.012, 0.4, 0.020, 0.03, 0.08),)),
    "second_sensor": Scenario(
        "second_sensor", "Baseline camera plus a second independent sensor, fused by inverse-variance weighting",
        (SensorModel((0.035, -0.025), 1.012, 0.4, 0.020, 0.03, 0.08),
         SensorModel((-0.030, 0.020), 0.990, -0.3, 0.025, 0.03, 0.08))),
    "markers": Scenario(
        "markers", "Camera reading fiducial markers placed at each grid point",
        (SensorModel((0.008, -0.006), 1.002, 0.1, 0.008, 0.0, 0.0),)),
}


def _measure(s: SensorModel, actual: np.ndarray, rng, n: int) -> np.ndarray:
    th = math.radians(s.rot_deg)
    A = s.scale * np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    base = A @ actual + np.array(s.bias_m)
    out = base + rng.normal(0, s.noise_m, (n, 2))
    bad = rng.random(n) < s.outlier_prob
    out[bad] += rng.normal(0, s.outlier_sd_m, (int(bad.sum()), 2))
    return out


def simulate(name: str, seed: int = 7, crit: Criteria = Criteria(), points_per_side: int = 5,
             readings_per_point: int = None, truth_error_m: float = 0.002) -> Readings:
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{name}'. Choices: {', '.join(SCENARIOS)}")
    sc = SCENARIOS[name]
    n = readings_per_point or crit.min_readings
    rng = np.random.default_rng([seed, sorted(SCENARIOS).index(name)])
    pts, true, meas = [], [], []
    pid = 0
    for j in range(points_per_side):
        for i in range(points_per_side):
            pid += 1
            t = np.array([i * crit.grid_spacing_m, j * crit.grid_spacing_m])
            actual = t + rng.normal(0, truth_error_m, 2)      # tape-measure and placement error
            reads = [_measure(s, actual, rng, n) for s in sc.sensors]
            if len(reads) == 1:
                fused = reads[0]
            else:
                w = np.array([1.0 / s.noise_m ** 2 for s in sc.sensors])
                fused = sum(wi * r for wi, r in zip(w, reads)) / w.sum()
            pts += [pid] * n
            true += [t] * n
            meas += list(fused)
    return Readings(name, np.array(pts), np.array(true), np.array(meas), source="simulated")
