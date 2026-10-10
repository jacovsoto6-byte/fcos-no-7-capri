"""Manufacturing order prioritization and scheduling.

Tracks orders and determines manufacturing and shipping priority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

from .core import ManufacturingOrder


@dataclass
class OrderSchedule:
    order_id: str
    item: str
    units: int
    needed_by: str
    priority: str
    status: str  # "pending", "in_progress", "ready_for_shipment", "shipped"
    manufacturing_start: Optional[str] = None
    estimated_completion: Optional[str] = None
    assigned_warehouse: Optional[str] = None


class ManufacturingScheduler:
    """Manages manufacturing orders and priority scheduling."""

    PRIORITY_WEIGHTS = {"high": 3.0, "medium": 2.0, "low": 1.0}
    PRODUCTION_RATE_UNITS_PER_DAY = 100

    def __init__(self):
        self.orders: Dict[str, OrderSchedule] = {}
        self.queue: List[OrderSchedule] = []

    def submit_order(self, order: ManufacturingOrder) -> OrderSchedule:
        """Submit a manufacturing order."""
        schedule = OrderSchedule(
            order_id=order.order_id,
            item=order.item,
            units=order.units,
            needed_by=order.needed_by,
            priority=order.priority,
            status="pending",
            assigned_warehouse=order.warehouse_name,
        )
        self.orders[order.order_id] = schedule
        self.queue.append(schedule)
        return schedule

    def prioritize_queue(self) -> List[OrderSchedule]:
        """Sort queue by priority and urgency."""
        now = datetime.now()

        def priority_score(order: OrderSchedule) -> float:
            priority_weight = self.PRIORITY_WEIGHTS.get(order.priority, 1.0)
            try:
                needed_date = datetime.strptime(order.needed_by, "%Y-%m-%d")
                days_until_due = (needed_date - now).days
                urgency = max(1.0, 30 - days_until_due)  # Higher score = more urgent
            except ValueError:
                urgency = 15.0
            return priority_weight * urgency

        self.queue = sorted(self.queue, key=priority_score, reverse=True)
        return self.queue

    def get_manufacturing_time(self, units: int) -> float:
        """Estimate manufacturing time in days."""
        return max(1.0, units / self.PRODUCTION_RATE_UNITS_PER_DAY)

    def start_manufacturing(self, order_id: str, start_date: str) -> bool:
        """Start manufacturing for an order."""
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        order.status = "in_progress"
        order.manufacturing_start = start_date

        mfg_time = self.get_manufacturing_time(order.units)
        from datetime import timedelta

        start = datetime.strptime(start_date, "%Y-%m-%d")
        completion = start + timedelta(days=mfg_time)
        order.estimated_completion = completion.strftime("%Y-%m-%d")

        return True

    def complete_manufacturing(self, order_id: str) -> bool:
        """Mark order as ready for shipment."""
        if order_id not in self.orders:
            return False
        self.orders[order_id].status = "ready_for_shipment"
        return True

    def ship_order(self, order_id: str) -> bool:
        """Mark order as shipped."""
        if order_id not in self.orders:
            return False
        self.orders[order_id].status = "shipped"
        return True

    def get_order_status(self, order_id: str) -> Optional[OrderSchedule]:
        """Get current order status."""
        return self.orders.get(order_id)

    def get_backlog(self) -> List[OrderSchedule]:
        """Get all pending and in-progress orders."""
        return [
            order
            for order in self.orders.values()
            if order.status in ["pending", "in_progress"]
        ]
