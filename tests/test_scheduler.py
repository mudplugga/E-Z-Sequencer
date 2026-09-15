import pytest

from retlu_ez_scheduler import EZMission, EZScheduler, MissionValidationError
from retlu_ez_scheduler.models import StepType


def test_build_m31_mission() -> None:
    plan = EZScheduler().build(
        EZMission(name="M31", target="M31", integration_minutes=120, exposure_seconds=180)
    )
    assert plan.frames == 40
    assert plan.steps[0].type is StepType.READINESS
    assert any(step.type is StepType.OPEN_ROOF for step in plan.steps)
    assert any(step.type is StepType.PLATE_SOLVE for step in plan.steps)
    assert any(step.type is StepType.CAPTURE for step in plan.steps)
    assert plan.steps[-1].type is StepType.CLOSE_ROOF


def test_rejects_invalid_exposure() -> None:
    with pytest.raises(MissionValidationError):
        EZScheduler().build(EZMission(name="Test", target="M31", exposure_seconds=0))


def test_home_altitude_is_45_degrees() -> None:
    plan = EZScheduler().build(EZMission(name="Test", target="M31"))
    home = next(step for step in plan.steps if step.type is StepType.HOME_MOUNT)
    assert home.parameters["home_altitude_deg"] == 45.0


def test_solar_requires_explicit_roof_policy() -> None:
    mission = EZMission(name="Sun", target="Sun", mission_type="solar")
    with pytest.raises(MissionValidationError):
        EZScheduler().build(mission)
