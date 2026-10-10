"""CLI for clever_moving: Full logistics orchestration.

Example:
    python -m clever_moving.cli --command coordinate --order-id ORD-001
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta

from .core import Address, Warehouse
from .coordinator import LogisticsCoordinator


def main() -> None:
    parser = argparse.ArgumentParser(description="clever_moving: Full logistics orchestration")
    parser.add_argument(
        "--command",
        choices=["coordinate", "status", "inspect", "warehouse-status"],
        default="coordinate",
    )
    parser.add_argument("--order-id", default="ORD-001")
    parser.add_argument("--origin-city", default="Dallas")
    parser.add_argument("--dest-city", default="Denver")
    parser.add_argument("--units", type=int, default=150)
    parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--vehicle-id", default="TRK-204")

    args = parser.parse_args()

    coordinator = LogisticsCoordinator()

    # Register default warehouse
    warehouse = Warehouse(
        name="North Hub",
        location=Address(city="Austin", state="TX", zip_code="78701", country="US"),
        capacity_units=500,
        available_units=300,
        handling_rate_per_hour=50.0,
    )
    coordinator.register_warehouse(warehouse)

    if args.command == "coordinate":
        # Coordinate a full shipment
        needed_by = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        
        plan = coordinator.coordinate_shipment(
            order_id=args.order_id,
            origin=Address(city=args.origin_city, state="TX", zip_code="75201", country="US"),
            destination=Address(city=args.dest_city, state="CO", zip_code="80202", country="US"),
            units=args.units,
            needed_by=needed_by,
            priority=args.priority,
            warehouse_name="North Hub",
            vehicle_id=args.vehicle_id,
            current_mileage=18000.0,
        )

        print(f"\n=== Logistics Coordination Plan ===")
        print(f"Order ID: {plan.order_id}")
        print(f"Route: {plan.best_route.name} ({plan.best_route.mode})")
        print(f"  Distance: {plan.best_route.distance_miles:.1f} miles")
        print(f"  ETA: {plan.best_route.estimated_days} days")
        print(f"  Cost: ${plan.best_route.cost:,.2f}")
        print(f"  Risk Level: {plan.best_route.risk_level}")
        print(f"\nWarehouse: {plan.warehouse_assignment}")
        print(f"  Utilization: {plan.warehouse_utilization:.1f}%")
        print(f"\nManufacturing Status: {plan.manufacturing_status.status}")
        print(f"  Needed by: {plan.manufacturing_status.needed_by}")
        print(f"\nVehicle Inspection: {plan.vehicle_inspection_status}")
        print(f"\nRisk Assessment")
        print(f"  Overall Risk: {plan.risk_assessment.overall_risk}")
        print(f"  Logistics Risk: {plan.risk_assessment.logistics_risk:.1f}")
        print(f"  Warehouse Risk: {plan.risk_assessment.warehouse_risk:.1f}")
        print(f"  Inspection Risk: {plan.risk_assessment.inspection_risk:.1f}")
        print(f"  Manufacturing Risk: {plan.risk_assessment.manufacturing_risk:.1f}")
        print(f"\nAction Items:")
        for i, action in enumerate(plan.action_items, 1):
            print(f"  {i}. {action}")

    elif args.command == "status":
        status = coordinator.get_shipment_status(args.order_id)
        if status:
            print(f"Order {args.order_id}: {status.status}")
        else:
            print(f"Order {args.order_id}: Not found")

    elif args.command == "inspect":
        fleet_health = coordinator.inspector.get_fleet_health()
        print(f"Fleet Health Report:")
        print(f"  Pass Rate: {fleet_health['pass_rate']:.1f}%")
        print(f"  Average Mileage: {fleet_health['average_mileage']:.1f} miles")
        print(f"  Vehicles Ready: {fleet_health['vehicles_ready']}")

    elif args.command == "warehouse-status":
        warehouse_mgr = coordinator.warehouses.get("North Hub")
        if warehouse_mgr:
            print(f"Warehouse: North Hub")
            print(f"  Total Capacity: {warehouse_mgr.warehouse.capacity_units} units")
            print(f"  Available: {warehouse_mgr.warehouse.available_units} units")
            print(f"  Utilization: {warehouse_mgr.get_utilization():.1f}%")
            print(f"  Handling Rate: {warehouse_mgr.warehouse.handling_rate_per_hour} units/hour")


if __name__ == "__main__":
    main()
