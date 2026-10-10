"""Supply chain risk assessment and shipment scoring.

Evaluates risks across logistics, warehouse, inspection, and manufacturing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .core import FreightPlan, Warehouse, VehicleInspection, ManufacturingOrder
from .fleet import FleetInspector
from .warehouse import WarehouseManager


@dataclass
class RiskScore:
    overall_risk: str  # "low", "medium", "high"
    logistics_risk: float  # 0-100
    warehouse_risk: float  # 0-100
    inspection_risk: float  # 0-100
    manufacturing_risk: float  # 0-100
    mitigation_steps: List[str]


class RiskAssessment:
    """Comprehensive supply chain risk assessment."""

    def __init__(
        self,
        freight_plan: FreightPlan,
        warehouse: WarehouseManager,
        inspector: FleetInspector,
        order: ManufacturingOrder,
    ):
        self.freight_plan = freight_plan
        self.warehouse = warehouse
        self.inspector = inspector
        self.order = order

    def assess(self) -> RiskScore:
        """Perform comprehensive risk assessment."""
        logistics_risk = self._assess_logistics_risk()
        warehouse_risk = self._assess_warehouse_risk()
        inspection_risk = self._assess_inspection_risk()
        manufacturing_risk = self._assess_manufacturing_risk()

        avg_risk = (logistics_risk + warehouse_risk + inspection_risk + manufacturing_risk) / 4.0
        overall_risk = "high" if avg_risk > 70 else "medium" if avg_risk > 40 else "low"

        mitigation_steps = self._generate_mitigations(
            logistics_risk, warehouse_risk, inspection_risk, manufacturing_risk
        )

        return RiskScore(
            overall_risk=overall_risk,
            logistics_risk=logistics_risk,
            warehouse_risk=warehouse_risk,
            inspection_risk=inspection_risk,
            manufacturing_risk=manufacturing_risk,
            mitigation_steps=mitigation_steps,
        )

    def _assess_logistics_risk(self) -> float:
        """Score logistics and shipping risk."""
        base_risk = {"low": 20.0, "medium": 50.0, "high": 80.0}.get(self.freight_plan.risk_level, 50.0)
        time_risk = max(0.0, (self.freight_plan.estimated_days - 3) * 10)
        cost_risk = min(100.0, (self.freight_plan.cost_estimate / 5000.0) * 100.0)
        return (base_risk * 0.5 + time_risk * 0.3 + cost_risk * 0.2)

    def _assess_warehouse_risk(self) -> float:
        """Score warehouse capacity and handling risk."""
        utilization = self.warehouse.get_utilization()
        capacity_risk = max(0.0, (utilization - 70.0) * 2.0)  # Risk increases above 70%
        handling_time = self.warehouse.estimated_handling_time(self.order.units)
        handling_risk = min(100.0, handling_time * 10.0)  # More time = more risk
        return (capacity_risk * 0.6 + handling_risk * 0.4)

    def _assess_inspection_risk(self) -> float:
        """Score vehicle inspection and fleet readiness risk."""
        fleet_health = self.inspector.get_fleet_health()
        pass_rate = fleet_health.get("pass_rate", 0.0)
        vehicles_ready = fleet_health.get("vehicles_ready", 0)

        readiness_risk = max(0.0, 100.0 - pass_rate)
        availability_risk = 0.0 if vehicles_ready > 0 else 100.0
        return (readiness_risk * 0.6 + availability_risk * 0.4)

    def _assess_manufacturing_risk(self) -> float:
        """Score manufacturing timeline and priority risk."""
        priority_risk = {"high": 60.0, "medium": 40.0, "low": 20.0}.get(self.order.priority, 40.0)
        # Risk increases if order is at low inventory levels
        inventory_risk = min(100.0, (100.0 - self.warehouse.get_utilization()) * 0.5)
        return (priority_risk * 0.6 + inventory_risk * 0.4)

    def _generate_mitigations(self, logistics: float, warehouse: float, inspection: float, manufacturing: float) -> List[str]:
        """Generate recommended mitigation steps."""
        steps = []
        if logistics > 60:
            steps.append("Consider expedited shipping or alternative routes to reduce logistics risk")
        if warehouse > 60:
            steps.append("Allocate additional warehouse space or defer non-urgent inbound shipments")
        if inspection > 60:
            steps.append("Perform emergency vehicle inspections and repairs before dispatch")
        if manufacturing > 60:
            steps.append("Prioritize manufacturing for high-priority orders and increase production capacity")
        if not steps:
            steps.append("Proceed with standard logistics and manufacturing procedures")
        return steps
