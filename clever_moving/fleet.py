"""Vehicle fleet inspection and compliance.

Manages vehicle health, defects, and inspection gating.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .core import VehicleInspection


@dataclass
class DefectSeverity:
    defect: str
    severity: str  # "critical", "major", "minor"


@dataclass
class InspectionReport:
    vehicle_id: str
    inspection_date: str
    passed: bool
    mileage: float
    defects: List[DefectSeverity] = field(default_factory=list)
    next_service_due: str = ""
    inspector_notes: str = ""


class FleetInspector:
    """Manages vehicle inspections and compliance."""

    CRITICAL_DEFECTS = {"brake_failure", "steering_failure", "tire_blowout", "engine_leak"}
    SERVICE_INTERVAL_MILES = 50000

    def __init__(self):
        self.inspections: Dict[str, InspectionReport] = {}
        self.fleet: Dict[str, VehicleInspection] = {}

    def inspect_vehicle(self, vehicle_id: str, mileage: float, defects: List[str], inspection_date: str) -> InspectionReport:
        """Perform a vehicle inspection."""
        severity_list = []
        critical_found = False

        for defect in defects:
            if defect in self.CRITICAL_DEFECTS:
                severity_list.append(DefectSeverity(defect=defect, severity="critical"))
                critical_found = True
            else:
                severity_list.append(DefectSeverity(defect=defect, severity="minor"))

        passed = not critical_found

        next_service = self._calculate_next_service(mileage)

        report = InspectionReport(
            vehicle_id=vehicle_id,
            inspection_date=inspection_date,
            passed=passed,
            mileage=mileage,
            defects=severity_list,
            next_service_due=next_service,
            inspector_notes="" if passed else "Vehicle failed inspection due to critical defects.",
        )

        self.inspections[vehicle_id] = report
        return report

    def _calculate_next_service(self, current_mileage: float) -> str:
        """Calculate next service mileage."""
        next_service_miles = current_mileage + self.SERVICE_INTERVAL_MILES
        return f"Service due at {int(next_service_miles):,} miles"

    def can_dispatch(self, vehicle_id: str) -> bool:
        """Check if vehicle is cleared for dispatch."""
        if vehicle_id not in self.inspections:
            return False
        report = self.inspections[vehicle_id]
        return report.passed and len([d for d in report.defects if d.severity == "critical"]) == 0

    def get_fleet_health(self) -> Dict[str, float]:
        """Get overall fleet health metrics."""
        if not self.inspections:
            return {"pass_rate": 0.0, "average_mileage": 0.0, "vehicles_ready": 0}

        total = len(self.inspections)
        passed = sum(1 for r in self.inspections.values() if r.passed)
        avg_mileage = sum(r.mileage for r in self.inspections.values()) / total if total > 0 else 0.0

        return {
            "pass_rate": (passed / total) * 100.0 if total > 0 else 0.0,
            "average_mileage": avg_mileage,
            "vehicles_ready": passed,
        }
