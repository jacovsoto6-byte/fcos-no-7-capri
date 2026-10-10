"""Integration layer: Full logistics coordination.

Orchestrates moving, shipping, warehousing, inspection, and manufacturing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .core import Address, FreightPlan, ManufacturingOrder, Warehouse, VehicleInspection
from .fleet import FleetInspector
from .manufacturing import ManufacturingScheduler, OrderSchedule
from .risk import RiskAssessment, RiskScore
from .route import RouteOptimizer, RouteOption
from .warehouse import WarehouseManager


@dataclass
class LogisticsCoordinationPlan:
    order_id: str
    freight_plan: FreightPlan
    best_route: RouteOption
    warehouse_assignment: str
    warehouse_utilization: float
    manufacturing_status: OrderSchedule
    vehicle_inspection_status: str
    risk_assessment: RiskScore
    action_items: List[str]


class LogisticsCoordinator:
    """Master orchestrator for full supply chain."""

    def __init__(self):
        self.warehouses: dict[str, WarehouseManager] = {}
        self.inspector = FleetInspector()
        self.scheduler = ManufacturingScheduler()
        self.route_optimizer = RouteOptimizer()

    def register_warehouse(self, warehouse: Warehouse) -> None:
        """Register a warehouse for coordination."""
        self.warehouses[warehouse.name] = WarehouseManager(warehouse)

    def coordinate_shipment(
        self,
        order_id: str,
        origin: Address,
        destination: Address,
        units: int,
        needed_by: str,
        priority: str,
        warehouse_name: str,
        vehicle_id: Optional[str] = None,
        current_mileage: float = 0.0,
    ) -> LogisticsCoordinationPlan:
        """Coordinate a complete shipment across all systems."""

        # Step 1: Generate route options
        route_options = self.route_optimizer.generate_options(origin, destination)
        best_route = route_options[0] if route_options else None

        # Step 2: Create manufacturing order
        manufacturing_order = ManufacturingOrder(
            order_id=order_id,
            item="product",
            units=units,
            needed_by=needed_by,
            priority=priority,
            warehouse_name=warehouse_name,
        )
        mfg_schedule = self.scheduler.submit_order(manufacturing_order)

        # Step 3: Check warehouse capacity
        warehouse_manager = self.warehouses.get(warehouse_name)
        if not warehouse_manager:
            raise ValueError(f"Warehouse {warehouse_name} not registered")

        warehouse_manager.reserve_space(units)
        warehouse_util = warehouse_manager.get_utilization()

        # Step 4: Vehicle inspection (if applicable)
        vehicle_status = "not_applicable"
        if vehicle_id:
            # Simulate inspection
            inspection_report = self.inspector.inspect_vehicle(
                vehicle_id, current_mileage, [], "2026-10-10"
            )
            vehicle_status = "passed" if inspection_report.passed else "failed"

        # Step 5: Create freight plan
        freight_plan = FreightPlan(
            origin=origin,
            destination=destination,
            mode=best_route.mode if best_route else "truck",
            estimated_days=best_route.estimated_days if best_route else 4,
            cost_estimate=best_route.cost if best_route else 2200.0,
            risk_level="low",
        )

        # Step 6: Risk assessment
        risk_assessor = RiskAssessment(
            freight_plan, warehouse_manager, self.inspector, manufacturing_order
        )
        risk_score = risk_assessor.assess()

        # Step 7: Generate action items
        action_items = [
            f"Assign {warehouse_name} for {units} units",
            f"Start manufacturing for order {order_id}",
            f"Schedule shipment via {best_route.mode if best_route else 'truck'}",
        ]
        if vehicle_status == "failed":
            action_items.append(f"ALERT: Vehicle {vehicle_id} failed inspection - repair before dispatch")
        if warehouse_util > 85:
            action_items.append("ALERT: Warehouse utilization critical - prioritize outbound")
        if risk_score.overall_risk == "high":
            action_items.extend(risk_score.mitigation_steps)

        return LogisticsCoordinationPlan(
            order_id=order_id,
            freight_plan=freight_plan,
            best_route=best_route or route_options[0],
            warehouse_assignment=warehouse_name,
            warehouse_utilization=warehouse_util,
            manufacturing_status=mfg_schedule,
            vehicle_inspection_status=vehicle_status,
            risk_assessment=risk_score,
            action_items=action_items,
        )

    def get_shipment_status(self, order_id: str) -> Optional[OrderSchedule]:
        """Get current status of a shipment."""
        return self.scheduler.get_order_status(order_id)

    def finalize_shipment(self, order_id: str) -> bool:
        """Mark order as shipped."""
        return self.scheduler.ship_order(order_id)
