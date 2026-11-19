# R2 Indoor Position Error: Risk Assessment

- Risk: **R2 Indoor localization** (chance Medium, impact High, owner Dayana)
- Plan response: Prevent: prototype onboard sensing early and measure position error
- Warning signal: Bench position error above 10 cm
- Pass criterion: error at most 10.0 cm at every grid point, at least 20 readings per point, tape-measured truth
- Generated (UTC): 2026-11-17T18:32:43+00:00  |  Module version 1.0.0

## demo_input_NOT_REAL_DATA: PASS

**Risk status:** Warning signal clear. R2 is reduced for this setup. Repeat if the sensor, lighting, or mounting changes.

| Check | Measured | Limit | Basis | Result |
|---|---|---|---|---|
| Worst-case error at every grid point | 3.3 cm | <= 10.0 cm | Slide | PASS |
| Readings at the least-sampled point | 20 readings | >= 20 readings | Slide | PASS |
| Grid points tested | 25 points | >= 9 points | Default (confirm) | PASS |

- Readings: 500 at 25 points. Mean error 1.3 cm, median 1.2 cm, 95th percentile 2.4 cm, worst 3.3 cm.
- Headroom: worst case is 67% below the limit.
- Overall bias (reading minus truth): x 0.8 cm, y -0.2 cm.
- 0 of 500 readings exceeded the limit. With 95% confidence, at most 0.5% of readings from this setup exceed it (assumes independent readings).

## Limits of this assessment

- Worst case over a few hundred readings is not a guarantee; rare bad detections can still occur in flight.
- The exceedance bound assumes independent readings. Readings taken at one static point share the same bias, so treat it as optimistic.
- Error is measured against a tape-measured position, which itself has a few millimetres of uncertainty.
- Bench error on a cart is not flight error: vibration, motion blur, and downwash are not tested here.
