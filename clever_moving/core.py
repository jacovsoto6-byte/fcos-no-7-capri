"""Core logistics planning for clever_moving.

This lightweight framework models moving, shipping, warehousing,
inspection, and manufacturing coordination in a single deterministic planner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal


@dataclass
class Address:
    city: str
    state: str
    zip_code: str
    country: str = "US"


@dataclass
class Warehouse:
    name: str
    location: Address
    capacity_units: int
    available_units: int
    handling_rate_per_hour: float = 25.0


@dataclass
class VehicleInspection:
    vehicle_id: str
    inspection_passed: bool
    mileage: float
    next_service_due: Optional[str] = None
    defects: List[str] = field(default_factory=list)


@dataclass
class FreightPlan:
    origin: Address
    destination: Address
    mode: Literal["truck", "rail", "air", "ocean"]
    estimated_days: int
    cost_estimate: float
    risk_level: Literal["low", "medium", "high"]


@dataclass
class ManufacturingOrder:
    order_id: str
    item: str
    units: int
    needed_by: str
    priority: Literal["low", "medium", "high"]
    warehouse_name: Optional[str] = None


@dataclass
class LogisticsPlan:
    freight_plan: FreightPlan
    warehouse: Warehouse
    inspection: Optional[VehicleInspection]
    manufacturing_order: Optional[ManufacturingOrder]
    route_summary: str
    recommended_action: str


def optimize_plan(
    freight_plan: FreightPlan,
    warehouse: Warehouse,
    inspection: Optional[VehicleInspection] = None,
    manufacturing_order: Optional[ManufacturingOrder] = None,
) -> LogisticsPlan:
    """Create a deterministic logistics recommendation for moving and shipping operations."""

    if warehouse.available_units < 1:
        recommended_action = "allocate overflow storage or defer inbound shipment"
    elif inspection and not inspection.inspection_passed:
        recommended_action = "repair vehicle before dispatch and reschedule inspection"
    elif manufacturing_order and manufacturing_order.priority == "high":
        recommended_action = "prioritize manufacturing deployment and fast-track outbound shipment"
    else:
        recommended_action = "dispatch according to schedule with standard warehouse handling"

    route_summary = (
        f"{freight_plan.mode.upper()} route from {freight_plan.origin.city} to {freight_plan.destination.city} "
        f"with {freight_plan.estimated_days}-day ETA and {freight_plan.risk_level} risk."
    )

    return LogisticsPlan(
        freight_plan=freight_plan,
        warehouse=warehouse,
        inspection=inspection,
        manufacturing_order=manufacturing_order,
        route_summary=route_summary,
        recommended_action=recommended_action,
    )


if __name__ == "__main__":
    warehouse = Warehouse(
        name="North Hub",
        location=Address(city="Austin", state="TX", zip_code="78701", country="US"),
        capacity_units=120,
        available_units=40,
        handling_rate_per_hour=28.0,
    )

    freight = FreightPlan(
        origin=Address(city="Dallas", state="TX", zip_code="75201", country="US"),
        destination=Address(city="Denver", state="CO", zip_code="80202", country="US"),
        mode="truck",
        estimated_days=4,
        cost_estimate=2200.0,
        risk_level="medium",
    )

    inspection = VehicleInspection(
        vehicle_id="TRK-204",
        inspection_passed=True,
        mileage=18000,
        defects=[],
    )

    manufacturing_order = ManufacturingOrder(
        order_id="MFG-1001",
        item="control panel kit",
        units=150,
        needed_by="2026-10-20",
        priority="high",
        warehouse_name="North Hub",
    )

    plan = optimize_plan(freight, warehouse, inspection, manufacturing_order)
    print(plan.route_summary)
    print(plan.recommended_action)
