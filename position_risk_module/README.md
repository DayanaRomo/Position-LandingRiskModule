# R2 Position Risk Assessment Module (Dayana Romo, Team I10)

Standalone module for the individual activity on plan slide 9: **bench test of onboard position
error (R2, indoor localization)**. It is separate from the calibration checkout module.

It takes position readings at tape-measured grid points, computes the error at each point, checks
the plan's limit (**at most 10 cm at every point, at least 20 readings per point**), says whether the
R2 warning signal is tripped, and estimates how often a reading would exceed the limit. It also
compares the two fixes your plan names: **add markers** or **add a second sensor**.

**Today it runs on simulated sensors** because there is no sensor yet. When the real sensor arrives,
log the bench readings to a CSV and run the same tool on them. Simulated results do not count as the
bench test, and every report says so.

## Run it

```powershell
python -m pip install -r requirements.txt
python -m position_risk                         # simulate baseline, second sensor, markers; compare
python -m position_risk --scenario baseline     # one setup (exit code 1 if it fails)
python -m position_risk --list-scenarios
python -m unittest discover -s tests -v         # 18 automated tests
```

## Use it on the real bench test

```powershell
python -m position_risk --make-template bench.csv      # blank sheet with the right columns
# fill bench.csv: one row per reading
python -m position_risk --csv bench.csv --out bench_run
python -m position_risk --csv bench.csv --units cm --out bench_run   # if you measured in cm
```

CSV columns: `point, x_true_m, y_true_m, x_meas_m, y_meas_m` (tape-measured position and the sensor's
reading, one row per reading). Exit code is 0 on PASS, 1 on FAIL, 2 on bad input.

## Outputs (in the output folder)

- `risk_assessment.md`: the report, with risk status, checks, headroom, and limits
- `risk_assessment.json`: the same results for other tools
- `<setup>_points.csv`, `<setup>_readings.csv`: per-point statistics and every reading
- `plot_map_<setup>.png`: grid map of worst error per point, red outline where the limit is broken
- `plot_error_distribution.png`: error histogram against the 10 cm limit

`sample_results/` has a full simulated comparison and a demo of the CSV path. The CSV demo uses
simulated numbers saved as a file, so it is **not real data**.

## What counts as a pass

| Check | Limit | Basis |
|---|---|---|
| Worst-case error at every grid point | <= 10 cm | Plan slide 9 (I4, P5) |
| Readings at the least-sampled point | >= 20 | Plan slide 9 |
| Grid points tested | >= 9 | Our default (confirm with your TA) |

The report also warns if the grid spacing differs from 0.5 m or points have uneven reading counts.

## Layout

```
position_risk/
  config.py   limit, minimums, and the R2 entry from the plan
  data.py     CSV loading and validation, blank template
  sim.py      simulated sensors: baseline, second_sensor, markers (assumed parameters)
  assess.py   per-point statistics, checks, risk status, exceedance bound
  report.py   markdown, JSON, CSV, and plots
  cli.py      command line
tests/        18 unit tests
```

## Honest limits

- The simulated sensor numbers (bias, noise, bad-detection rate) are assumptions, not measurements.
- A worst case over a few hundred readings is not a guarantee; rare bad detections can still happen in flight.
- The 95% exceedance bound assumes independent readings. Readings at one static point share a bias, so it is optimistic.
- Bench error on a cart is not flight error. Vibration, motion blur, and downwash are not tested.
- The code was written with an AI coding assistant (Claude), like the team's other modules.
