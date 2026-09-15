# RETLU E-Z Scheduler

**RETLU — Explore, Observe, Understand**

RETLU E-Z Scheduler is the beginner-friendly mission planning engine for RETLU. It turns a small set of astronomical goals into a clear, validated imaging mission without exposing the user to driver or protocol complexity.

## Principle

> Tell RETLU what you want to photograph. RETLU works out the sequence.

The scheduler is deliberately independent of Alpaca, INDI, camera drivers and the GUI. It produces a mission plan that Mission Control can execute through RETLU-Core interfaces.

## First foundation

- target and mission models
- simple imaging plan generation
- validation and safety gates
- JSON save/load
- explicit execution steps
- no hardware/protocol dependencies

## Example

```python
mission = EZMission(
    name="M31",
    target="M31",
    integration_minutes=120,
    exposure_seconds=180,
)
plan = EZScheduler().build(mission)
```

The resulting plan contains the normal RETLU flow: readiness, roof, mount home, slew, plate solve, focus, guiding, capture, dither, recovery and safe shutdown.

**Blocks communicate through interfaces, never through implementation.**
