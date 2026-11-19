# R2 Indoor Position Error: Risk Assessment

> **SIMULATED DATA.** The numbers below come from a software model of the sensors. They test this tool and the plan's decision logic. They do not count as the bench test and say nothing about real hardware.

- Risk: **R2 Indoor localization** (chance Medium, impact High, owner Dayana)
- Plan response: Prevent: prototype onboard sensing early and measure position error
- Warning signal: Bench position error above 10 cm
- Pass criterion: error at most 10.0 cm at every grid point, at least 20 readings per point, tape-measured truth
- Generated (UTC): 2026-11-18T22:33:57+00:00  |  Module version 1.0.0

## Comparison

| Setup | Worst error (cm) | Mean error (cm) | Points over limit | Readings over limit | 95% upper bound on exceedance | Result |
|---|---|---|---|---|---|---|
| baseline | 19.2 | 4.9 | 7 of 25 | 9 of 500 | 3.1% | **FAIL** |
| second_sensor | 13.3 | 2.5 | 2 of 25 | 2 of 500 | 1.2% | **FAIL** |
| markers | 4.4 | 1.2 | 0 of 25 | 0 of 500 | 0.5% | PASS |

## baseline: FAIL

**Risk status:** WARNING SIGNAL TRIPPED (simulated). Add markers or a second sensor and retest. Tell the team immediately (plan slide 3).

| Check | Measured | Limit | Basis | Result |
|---|---|---|---|---|
| Worst-case error at every grid point | 19.2 cm | <= 10.0 cm | Slide | **FAIL** |
| Readings at the least-sampled point | 20 readings | >= 20 readings | Slide | PASS |
| Grid points tested | 25 points | >= 9 points | Default (confirm) | PASS |

- Readings: 500 at 25 points. Mean error 4.9 cm, median 4.7 cm, 95th percentile 8.7 cm, worst 19.2 cm.
- Headroom: worst case is 92% above the limit.
- Overall bias (reading minus truth): x 3.9 cm, y -0.6 cm.
- 9 of 500 readings exceeded the limit. With 95% confidence, at most 3.1% of readings from this setup exceed it (assumes independent readings).
- Failing points (worst five): point 16 at (0.0, 1.5) m, worst 19.2 cm; point 14 at (1.5, 1.0) m, worst 17.9 cm; point 21 at (0.0, 2.0) m, worst 17.6 cm; point 19 at (1.5, 1.5) m, worst 15.3 cm; point 25 at (2.0, 2.0) m, worst 15.2 cm
- Note: SIMULATED DATA: these results test the software and do not count as the bench test.

## second_sensor: FAIL

**Risk status:** WARNING SIGNAL TRIPPED (simulated). Add markers or a second sensor and retest. Tell the team immediately (plan slide 3).

| Check | Measured | Limit | Basis | Result |
|---|---|---|---|---|
| Worst-case error at every grid point | 13.3 cm | <= 10.0 cm | Slide | **FAIL** |
| Readings at the least-sampled point | 20 readings | >= 20 readings | Slide | PASS |
| Grid points tested | 25 points | >= 9 points | Default (confirm) | PASS |

- Readings: 500 at 25 points. Mean error 2.5 cm, median 2.2 cm, 95th percentile 5.3 cm, worst 13.3 cm.
- Headroom: worst case is 33% above the limit.
- Overall bias (reading minus truth): x 1.1 cm, y -0.2 cm.
- 2 of 500 readings exceeded the limit. With 95% confidence, at most 1.2% of readings from this setup exceed it (assumes independent readings).
- Failing points (worst five): point 25 at (2.0, 2.0) m, worst 13.3 cm; point 4 at (1.5, 0.0) m, worst 11.7 cm
- Note: SIMULATED DATA: these results test the software and do not count as the bench test.

## markers: PASS

**Risk status:** Warning signal clear (simulated). Keep this sensor setup. Repeat the test on the real sensor and bench grid.

| Check | Measured | Limit | Basis | Result |
|---|---|---|---|---|
| Worst-case error at every grid point | 4.4 cm | <= 10.0 cm | Slide | PASS |
| Readings at the least-sampled point | 20 readings | >= 20 readings | Slide | PASS |
| Grid points tested | 25 points | >= 9 points | Default (confirm) | PASS |

- Readings: 500 at 25 points. Mean error 1.2 cm, median 1.2 cm, 95th percentile 2.4 cm, worst 4.4 cm.
- Headroom: worst case is 56% below the limit.
- Overall bias (reading minus truth): x 0.7 cm, y -0.2 cm.
- 0 of 500 readings exceeded the limit. With 95% confidence, at most 0.5% of readings from this setup exceed it (assumes independent readings).
- Note: SIMULATED DATA: these results test the software and do not count as the bench test.

## Limits of this assessment

- Worst case over a few hundred readings is not a guarantee; rare bad detections can still occur in flight.
- The exceedance bound assumes independent readings. Readings taken at one static point share the same bias, so treat it as optimistic.
- Error is measured against a tape-measured position, which itself has a few millimetres of uncertainty.
- Bench error on a cart is not flight error: vibration, motion blur, and downwash are not tested here.
