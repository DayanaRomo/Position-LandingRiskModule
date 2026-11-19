# Presenter Guide: R2 Indoor Position Error (Dayana Romo)

Everything you need to present your individual activity. Read sections 1 to 3 first; they are the
presentation. Sections 4 to 8 are backup.

---

## 1. The 20-second version

"My risk is R2: without GPS, the drone must know where it is within 10 cm so it can land on a pad.
My activity is a bench test of position error. We have no sensor yet, so I built the tool that will
run the test, and I checked it on simulated sensors. In simulation a camera alone fails the 10 cm
limit, and markers fix it. That is not a real result, so the real bench test is still ahead."

---

## 2. Slide content (same table format as your other slides)

**Label:** INDIVIDUAL ACTIVITY · R2 LOCALIZATION
**Title:** Dayana Romo: Indoor Position Error (Simulated Tool)

| Row | Text |
|---|---|
| Risk it reduces | R2, indoor localization. The drone needs position error of at most 10 cm with no GPS so it can land on a pad (I4, P5) |
| What I built | A Python tool that takes position readings at tape-measured grid points, checks the 10 cm limit at every point, and compares fixes: markers or a second sensor |
| Setup | Plan setup: 0.5 m grid, at least 20 readings per point. No sensor yet, so a seeded simulator supplies readings; the same tool will read real bench data from a CSV |
| Pass criterion | Error at most 10 cm at every grid point, at least 20 readings per point (plan slide 9) |
| If it fails | Add markers or a second sensor and retest (plan slide 9) |
| Result | Simulated only. Camera alone fails (worst 19.2 cm). Second sensor still fails (13.3 cm). Markers pass (4.4 cm). Real bench test still to do |

**Speaker notes to paste:** "Built by Dayana Romo with an AI coding assistant (Claude). All numbers are from a simulator with assumed sensor parameters, so they test the tool and the decision logic, not the real sensor. The real bench test will use the same tool on measured data."

Want it added to the deck? Ask and I will build it in the same style.

---

## 3. Two-and-a-half minute script

1. **Risk (30 s).** "R2 is indoor localization. There is no GPS inside the facility, so the drone has to find a pad using onboard sensing, and it must be within 10 cm. We rated the chance Medium and the impact High. My plan response is to prototype the sensing early and measure the error. The warning signal is any bench error above 10 cm."
2. **Test plan (30 s).** "The bench test is a marked grid with 0.5 meter spacing. I put the sensor at each point, take at least 20 readings, and compare every reading with the tape-measured position. It passes only if the error is 10 cm or less at every point, because one bad reading at a landing is enough to miss the pad. If it fails, the plan says add markers or a second sensor."
3. **What I built (30 s).** "I built the tool that analyzes that test. It gives the error at each point, checks the limit, says whether the warning signal is tripped, and estimates how often a reading would exceed 10 cm. It also compares the two fixes from the plan."
4. **Simulated results (45 s).** "We have no sensor yet, so I ran it on simulated sensors. A camera alone fails: the worst error is 19.2 cm and 7 of 25 points break the limit. Adding a second sensor helps, 13.3 cm, but still fails. Markers pass at 4.4 cm. I reran each setup 200 times with different random seeds: camera alone never passed, markers always passed, and the second sensor passed 7% of the time."
5. **Honest limit (15 s).** "These numbers come from sensor values I assumed, not measurements. They show the tool works. They are not the bench test."
6. **Next step (10 s).** "When the sensor arrives, I log the readings in a CSV and run one command. If the real sensor behaves like the camera-only case, markers are the first thing I will try."

---

## 4. Numbers to know

| Setup (seed 7) | Worst error | Mean error | Points over 10 cm | Readings over 10 cm | 95% upper bound | Result |
|---|---|---|---|---|---|---|
| Camera only (baseline) | 19.2 cm | 4.9 cm | 7 of 25 | 9 of 500 | 3.1% | FAIL |
| Camera + second sensor | 13.3 cm | 2.5 cm | 2 of 25 | 2 of 500 | 1.2% | FAIL |
| Camera + markers | 4.4 cm | 1.2 cm | 0 of 25 | 0 of 500 | 0.5% | PASS |

Over 200 reruns (different seeds): camera only passes 0% (median worst case 21.8 cm); second sensor
passes 7% (13.2 cm); markers pass 100% (3.6 cm).

How to read "95% upper bound": with 95% confidence, no more than that share of readings from this
setup exceed 10 cm. With zero failures in 500 readings it is about 0.5%; it is a rough "rule of three"
style bound, and it is optimistic because readings at one point share a bias.

Why mean error alone is not enough: the baseline's mean is 4.9 cm, comfortably under 10 cm, yet it
fails. Landing depends on the worst reading, not the average.

---

## 5. Live demo (about 60 seconds)

```powershell
cd <folder that contains position_risk>
python -m position_risk --out demo
notepad demo\risk_assessment.md
explorer demo
```

Show: the Comparison table at the top of the report, then `plot_map_baseline.png` (red outlines are
the points over 10 cm), then `plot_error_distribution.png` (the baseline's tail crosses the red line,
markers do not).

If the demo fails to start, show `sample_results\simulated_comparison\` instead; it has the same files.

---

## 6. What happens when the real sensor arrives

1. Mark a grid with 0.5 m spacing (5 x 5 gives 25 points; the tool needs at least 9). Tape-measure each point.
2. Mount the sensor on the cart or tether. Keep everything stationary at each point. No flight; follow the plan's safety rules (slide 13).
3. At each point record at least 20 readings and the tape-measured position into a CSV: `point, x_true_m, y_true_m, x_meas_m, y_meas_m`. Make a blank sheet with `python -m position_risk --make-template bench.csv`.
4. Run `python -m position_risk --csv bench.csv --out bench_run` (add `--units cm` if you measured in centimeters).
5. Read `bench_run\risk_assessment.md`. If it says WARNING SIGNAL TRIPPED, tell the team immediately, apply the fix (markers or a second sensor), and retest.
6. Then update the slide's Result row with the real numbers and drop "(Simulated Tool)" from the title.

---

## 7. Questions you may get, with honest answers

**Is this your bench test?** No. It is the tool for the bench test, checked on simulated data. The real test needs the real sensor.

**Where do the simulated numbers come from?** I assumed them: a constant offset, random noise, and a small rate of bad detections for a camera. I did not measure them. They are chosen to be plausible, and they decide which setup passes, so I do not claim the simulated outcome predicts the real one.

**Why worst case, not average?** The plan says at most 10 cm at every point, and a landing happens at one moment. A single large error can miss the pad even if the average is small.

**Why at least 20 readings per point?** That is the plan's minimum. More readings tighten the estimate of how often a bad reading happens.

**What is the 95% bound?** A statistical ceiling on how often a reading could exceed 10 cm, given how many we took. It assumes independent readings, so it is optimistic for a static sensor.

**Why did the second sensor not fix it?** In the simulation, averaging two sensors cuts random noise by about 30% and halves the size of a single bad detection, but the combined worst case is still over 10 cm most of the time. Markers fix the cause by making each detection more accurate. With a real sensor this could differ.

**How is this different from your calibration module?** The calibration module is a broad pre-flight checklist with seven tests. This one is only R2, goes deeper, compares the plan's two fixes, and reads real bench data from a CSV.

**Is 10 cm the right limit?** It comes from the plan (I4, P5), where the criteria are proposed and still need Technical TA approval.

**Did you write the code yourself?** It was written with an AI coding assistant (Claude), like the team's other modules, and the slide notes say so. Be ready to explain the steps in section 8 in your own words.

**What does it not test?** Flight. Vibration, motion blur, and downwash from the propellers are not included in a bench test.

---

## 8. How the code works (explain it in your own words)

1. **Input:** one row per reading: point number, tape-measured position, sensor reading.
2. **Error:** for each reading, the straight-line distance between the sensor reading and the tape-measured position.
3. **Per point:** mean, 95th percentile, and worst error, plus the average direction of the error (bias).
4. **Checks:** worst error at every point must be at most 10 cm; every point needs at least 20 readings; at least 9 points. The first two come from your plan, the third is our default.
5. **Risk status:** if the worst error is over 10 cm the plan's warning signal is tripped and the report states the plan's response (add markers or a second sensor).
6. **Exceedance bound:** counts readings over 10 cm and gives a 95% upper bound on how often that could happen (Wilson interval).
7. **Simulation:** a seeded random sensor model with a bias, scale and rotation error, noise, and occasional bad detections. Markers lower the noise and remove bad detections; a second sensor is averaged with the first.
8. **Output:** a markdown report, JSON, CSVs, and plots, and an exit code (0 pass, 1 fail, 2 bad input).

Tests: 18 automated tests check the 10 cm edge (exactly 10.0 passes, 10.1 fails), the 20-reading rule, CSV loading and bad-input errors, unit conversion, and that the simulated setups behave consistently over 40 seeds.

---

## 9. Checklist before you present

- [ ] Confirm with your Technical TA that the 10 cm limit and the grid plan are approved (plan slide 6 says they are proposed).
- [ ] Say "simulated" out loud, early and more than once.
- [ ] Run the demo once on the machine you will present from. If the course wants the target environment, run it on the Linux machine.
- [ ] Open `sample_results\simulated_comparison\` as a backup.
- [ ] Do not describe the simulated result as the bench result, even in passing.
- [ ] Know the three numbers: 19.2 cm, 13.3 cm, 4.4 cm, and why mean error is not the pass test.
