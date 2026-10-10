"""CLI for clever_moving.

Example:
    python -m clever_moving.cli
"""

from __future__ import annotations

import argparse

from .core import Address, FreightPlan, ManufacturingOrder, VehicleInspection, Warehouse, optimize_plan


def main() -> None:
    parser = argparse.ArgumentParser(description="clever_moving logistics coordinator")
    parser.add_argument("--origin-city", default="Dallas")
    parser.add_argument("--dest-city", default="Denver")
    parser.add_argument("--mode", choices=["truck", "rail", "air", "ocean"], default="truck")
    parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium")
    args = parser.parse_args()

    warehouse = Warehouse(
        name="North Hub",
        location=Address(city="Austin", state="TX", zip_code="78701", country="US"),
        capacity_units=120,
        available_units=40,
        handling_rate_per_hour=28.0,
    )

    freight = FreightPlan(
        origin=Address(city=args.origin_city, state="TX", zip_code="75201", country="US"),
        destination=Address(city=args.dest_city, state="CO", zip_code="80202", country="US"),
        mode=args.mode,
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
        priority=args.priority,
        warehouse_name="North Hub",
    )

    plan = optimize_plan(freight, warehouse, inspection, manufacturing_order)
    print(plan.route_summary)
    print(plan.recommended_action)


if __name__ == "__main__":
    main()
