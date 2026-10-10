"""clever_moving

A logistics and manufacturing coordination package for:
- clever moving services
- supply shipping and freight coordination
- warehouse management
- vehicle inspection and compliance
- manufacturing services orchestration
"""

from .core import (
    Address, Warehouse, VehicleInspection, FreightPlan, ManufacturingOrder,
    LogisticsPlan, optimize_plan
)

__all__ = [
    "Address",
    "Warehouse",
    "VehicleInspection",
    "FreightPlan",
    "ManufacturingOrder",
    "LogisticsPlan",
    "optimize_plan",
]
__version__ = "0.1.0"
