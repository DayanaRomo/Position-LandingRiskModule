"""Run with:  python -m unittest discover -s tests -v   (standard library + numpy)"""
import csv
import json
import os
import tempfile
import unittest

import numpy as np

from position_risk.assess import assess, risk_status, wilson_upper
from position_risk.cli import main
from position_risk.config import Criteria
from position_risk.data import Readings, load_csv, write_csv, write_template
from position_risk.sim import SCENARIOS, simulate


def synthetic(err_m, n=20, side=3, spacing=0.5):
    """Perfect grid where every reading is off by exactly err_m along x."""
    pts, true, meas = [], [], []
    pid = 0
    for j in range(side):
        for i in range(side):
            pid += 1
            for _ in range(n):
                pts.append(pid); true.append([i * spacing, j * spacing]); meas.append([i * spacing + err_m, j * spacing])
    return Readings("synthetic", np.array(pts), np.array(true), np.array(meas), source="csv")


class TestAssess(unittest.TestCase):
    def test_exact_errors_pass_and_fail_at_the_limit(self):
        self.assertTrue(assess(synthetic(0.099)).passed)
        self.assertTrue(assess(synthetic(0.100)).passed)      # limit is inclusive
        self.assertFalse(assess(synthetic(0.101)).passed)

    def test_one_bad_reading_fails_that_point_only(self):
        r = synthetic(0.01)
        r.meas[0] += [0.2, 0.0]
        a = assess(r)
        self.assertFalse(a.passed)
        self.assertEqual([p.point for p in a.failing_points], [1])
        self.assertEqual(a.n_exceed, 1)
        self.assertTrue(a.warning_signal_tripped)

    def test_too_few_readings_fails_even_if_accurate(self):
        a = assess(synthetic(0.01, n=19))
        self.assertFalse(a.passed)
        self.assertEqual(a.checks[1].passed, False)

    def test_too_few_points_fails(self):
        a = assess(synthetic(0.01, side=2))      # 4 points, default needs 9
        self.assertFalse(a.passed)

    def test_wilson_bound(self):
        self.assertAlmostEqual(wilson_upper(0, 500), 0.0053, places=3)    # near rule of three (3/500 = 0.006)
        self.assertGreater(wilson_upper(5, 500), 5 / 500)
        self.assertEqual(wilson_upper(0, 0), 1.0)

    def test_grid_spacing_warning(self):
        a = assess(synthetic(0.01, spacing=0.25))
        self.assertTrue(any("spacing" in w for w in a.warnings))

    def test_simulated_data_is_flagged(self):
        a = assess(simulate("markers"))
        self.assertTrue(any("SIMULATED" in w for w in a.warnings))
        self.assertIn("simulated", risk_status(a)["status"])
        b = assess(synthetic(0.01))
        self.assertNotIn("simulated", risk_status(b)["status"])


class TestScenarios(unittest.TestCase):
    def test_baseline_fails_markers_pass_across_seeds(self):
        for seed in range(40):
            self.assertFalse(assess(simulate("baseline", seed)).passed, seed)
            self.assertTrue(assess(simulate("markers", seed)).passed, seed)

    def test_second_sensor_improves_on_baseline(self):
        b = [assess(simulate("baseline", s)).worst_err_m for s in range(40)]
        f = [assess(simulate("second_sensor", s)).worst_err_m for s in range(40)]
        self.assertLess(np.median(f), np.median(b))

    def test_same_seed_same_result(self):
        a1, a2 = simulate("baseline", 3), simulate("baseline", 3)
        self.assertTrue(np.array_equal(a1.meas, a2.meas))

    def test_unknown_scenario_rejected(self):
        with self.assertRaises(ValueError):
            simulate("nope")


class TestData(unittest.TestCase):
    def test_csv_round_trip_and_units(self):
        r = simulate("markers", 1)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.csv")
            write_csv(p, r)
            back = load_csv(p)
            self.assertTrue(np.allclose(back.meas, r.meas, atol=1e-5))
            # same numbers declared as centimetres are 100x smaller
            small = load_csv(p, units="cm")
            self.assertTrue(np.allclose(small.meas, r.meas * 0.01, atol=1e-6))

    def test_bad_csv_is_rejected_with_clear_error(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "bad.csv")
            with open(p, "w") as f:
                f.write("point,x_true_m\n1,0.0\n")
            with self.assertRaises(ValueError) as cm:
                load_csv(p)
            self.assertIn("missing columns", str(cm.exception))
            p2 = os.path.join(d, "nan.csv")
            with open(p2, "w") as f:
                f.write("point,x_true_m,y_true_m,x_meas_m,y_meas_m\n1,0,0,abc,0\n")
            with self.assertRaises(ValueError):
                load_csv(p2)

    def test_template_loads(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.csv")
            write_template(p)
            self.assertEqual(len(load_csv(p).point), 3)


class TestCli(unittest.TestCase):
    def test_comparison_run_writes_everything(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(main(["--out", d, "--no-plots"]), 0)
            for f in ["risk_assessment.md", "risk_assessment.json", "baseline_points.csv", "markers_readings.csv"]:
                self.assertGreater(os.path.getsize(os.path.join(d, f)), 0, f)
            doc = json.load(open(os.path.join(d, "risk_assessment.json")))
            self.assertEqual(len(doc["assessments"]), 3)
            self.assertEqual(doc["risk"]["id"], "R2")

    def test_single_run_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(main(["--scenario", "markers", "--out", os.path.join(d, "a"), "--no-plots"]), 0)
            self.assertEqual(main(["--scenario", "baseline", "--out", os.path.join(d, "b"), "--no-plots"]), 1)

    def test_real_data_path(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "bench.csv")
            write_csv(p, synthetic(0.02))
            self.assertEqual(main(["--csv", p, "--out", os.path.join(d, "o"), "--no-plots"]), 0)
            md = open(os.path.join(d, "o", "risk_assessment.md")).read()
            self.assertNotIn("SIMULATED DATA", md)
            write_csv(p, synthetic(0.15))
            self.assertEqual(main(["--csv", p, "--out", os.path.join(d, "o2"), "--no-plots"]), 1)

    def test_bad_input_exit_code_2(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "bad.csv")
            open(p, "w").write("a,b\n1,2\n")
            self.assertEqual(main(["--csv", p, "--out", os.path.join(d, "o"), "--no-plots"]), 2)


if __name__ == "__main__":
    unittest.main()
