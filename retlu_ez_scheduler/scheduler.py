from __future__ import annotations

import json
import math
from pathlib import Path

from .models import EZMission, MissionPlan, MissionStep, MissionType, SchedulerSettings, StepType


class MissionValidationError(ValueError):
    """Raised when an E-Z mission cannot safely be scheduled."""


class EZScheduler:
    """Build simple, deterministic RETLU imaging missions."""

    def __init__(self, settings: SchedulerSettings | None = None) -> None:
        self.settings = settings or SchedulerSettings()

    def validate(self, mission: EZMission) -> None:
        if not mission.name.strip():
            raise MissionValidationError("Mission name is required")
        if not mission.target.strip():
            raise MissionValidationError("Target is required")
        if mission.integration_minutes <= 0:
            raise MissionValidationError("Integration time must be greater than zero")
        if mission.exposure_seconds <= 0:
            raise MissionValidationError("Exposure must be greater than zero")
        if mission.exposure_seconds > 3600:
            raise MissionValidationError("Exposure cannot exceed 3600 seconds")
        if not 0 <= mission.minimum_altitude_deg <= 90:
            raise MissionValidationError("Minimum altitude must be between 0 and 90 degrees")
        if mission.mission_type is MissionType.SOLAR and mission.automatic_roof:
            raise MissionValidationError("Solar missions require explicit observatory safety policy")

    def build(self, mission: EZMission) -> MissionPlan:
        self.validate(mission)
        frames = max(1, math.ceil(mission.integration_minutes * 60 / mission.exposure_seconds))
        estimated_minutes = frames * mission.exposure_seconds / 60
        steps: list[MissionStep] = [
            MissionStep(StepType.READINESS, "Check RETLU observatory readiness", safety_critical=True),
        ]

        if mission.automatic_roof:
            steps.append(
                MissionStep(
                    StepType.OPEN_ROOF,
                    "Open roof and verify open sensor",
                    {"timeout_seconds": self.settings.roof_open_timeout_seconds},
                    safety_critical=True,
                )
            )

        steps.extend(
            [
                MissionStep(
                    StepType.HOME_MOUNT,
                    "Home telescope",
                    {"home_altitude_deg": self.settings.home_altitude_deg},
                    safety_critical=True,
                ),
                MissionStep(
                    StepType.SLEW,
                    f"Slew to {mission.target}",
                    {"target": mission.target},
                    safety_critical=True,
                ),
            ]
        )

        if mission.plate_solving:
            steps.append(MissionStep(StepType.PLATE_SOLVE, "Plate solve and centre target"))
        if mission.autofocus:
            steps.append(MissionStep(StepType.FOCUS, "Autofocus"))
        if mission.guiding:
            steps.append(MissionStep(StepType.START_GUIDING, "Start guiding and verify stability"))

        steps.append(
            MissionStep(
                StepType.CAPTURE,
                f"Capture {frames} light frames",
                {"frames": frames, "exposure_seconds": mission.exposure_seconds},
            )
        )

        if mission.dithering:
            steps.append(MissionStep(StepType.DITHER, "Dither between suitable light frames"))
        if mission.autofocus and self.settings.refocus_interval_minutes > 0:
            steps.append(
                MissionStep(
                    StepType.REFOCUS,
                    "Refocus when the configured interval is reached",
                    {"interval_minutes": self.settings.refocus_interval_minutes},
                )
            )

        steps.extend(
            [
                MissionStep(StepType.SAFETY_CHECK, "Continuous weather, roof and mount safety check", safety_critical=True),
                MissionStep(StepType.PARK, "Park telescope", safety_critical=True),
            ]
        )
        if mission.automatic_roof:
            steps.append(
                MissionStep(
                    StepType.CLOSE_ROOF,
                    "Close roof and verify closed sensor",
                    {"timeout_seconds": self.settings.roof_close_timeout_seconds},
                    safety_critical=True,
                )
            )

        return MissionPlan(mission, frames, estimated_minutes, steps)

    @staticmethod
    def save(plan: MissionPlan, path: str | Path) -> None:
        Path(path).write_text(json.dumps(plan.to_dict(), indent=2), encoding="utf-8")
