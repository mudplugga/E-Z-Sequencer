from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class MissionType(StrEnum):
    DEEP_SKY = "deep_sky"
    MOON = "moon"
    PLANET = "planet"
    SOLAR = "solar"
    CALIBRATION = "calibration"


class StepType(StrEnum):
    READINESS = "readiness"
    OPEN_ROOF = "open_roof"
    HOME_MOUNT = "home_mount"
    SLEW = "slew"
    PLATE_SOLVE = "plate_solve"
    FOCUS = "focus"
    START_GUIDING = "start_guiding"
    CAPTURE = "capture"
    DITHER = "dither"
    REFOCUS = "refocus"
    SAFETY_CHECK = "safety_check"
    PARK = "park"
    CLOSE_ROOF = "close_roof"


@dataclass(slots=True)
class EZMission:
    name: str
    target: str
    integration_minutes: float = 60.0
    exposure_seconds: float = 180.0
    mission_type: MissionType = MissionType.DEEP_SKY
    guiding: bool = True
    dithering: bool = True
    autofocus: bool = True
    plate_solving: bool = True
    automatic_roof: bool = True
    minimum_altitude_deg: float = 30.0
    start_altitude_deg: float | None = None
    end_altitude_deg: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SchedulerSettings:
    roof_open_timeout_seconds: float = 5.0
    roof_close_timeout_seconds: float = 30.0
    safety_check_interval_seconds: float = 10.0
    refocus_interval_minutes: float = 60.0
    home_altitude_deg: float = 45.0


@dataclass(slots=True)
class MissionStep:
    type: StepType
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    safety_critical: bool = False


@dataclass(slots=True)
class MissionPlan:
    mission: EZMission
    frames: int
    estimated_minutes: float
    steps: list[MissionStep]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["mission"]["mission_type"] = self.mission.mission_type.value
        for step in data["steps"]:
            step["type"] = step["type"].value
        return data
