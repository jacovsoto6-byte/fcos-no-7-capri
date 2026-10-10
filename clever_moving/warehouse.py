"""Warehouse management and capacity planning.

Tracks inventory, allocation, and handling throughput.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .core import Address, Warehouse


@dataclass
class InventoryItem:
    sku: str
    name: str
    quantity: int
    location: str


@dataclass
class WarehouseTransaction:
    tx_id: str
    warehouse_name: str
    tx_type: str  # "inbound", "outbound", "internal"
    item_sku: str
    quantity: int
    timestamp: str


class WarehouseManager:
    """Manages warehouse inventory and allocation."""

    def __init__(self, warehouse: Warehouse):
        self.warehouse = warehouse
        self.inventory: Dict[str, InventoryItem] = {}
        self.transaction_log: List[WarehouseTransaction] = []

    def allocate_space(self, units_needed: int) -> bool:
        """Check if warehouse has capacity."""
        return self.warehouse.available_units >= units_needed

    def reserve_space(self, units: int) -> bool:
        """Reserve space in warehouse."""
        if self.allocate_space(units):
            self.warehouse.available_units -= units
            return True
        return False

    def release_space(self, units: int) -> None:
        """Release reserved space."""
        self.warehouse.available_units = min(
            self.warehouse.available_units + units, self.warehouse.capacity_units
        )

    def estimated_handling_time(self, units: int) -> float:
        """Estimate hours to process units."""
        return units / max(self.warehouse.handling_rate_per_hour, 1.0)

    def add_inventory(self, sku: str, name: str, quantity: int, location: str) -> None:
        """Add items to inventory."""
        if sku in self.inventory:
            self.inventory[sku].quantity += quantity
        else:
            self.inventory[sku] = InventoryItem(sku=sku, name=name, quantity=quantity, location=location)

    def remove_inventory(self, sku: str, quantity: int) -> bool:
        """Remove items from inventory."""
        if sku in self.inventory and self.inventory[sku].quantity >= quantity:
            self.inventory[sku].quantity -= quantity
            return True
        return False

    def get_utilization(self) -> float:
        """Get warehouse utilization percentage."""
        used = self.warehouse.capacity_units - self.warehouse.available_units
        return (used / max(self.warehouse.capacity_units, 1)) * 100.0

    def log_transaction(
        self, tx_id: str, tx_type: str, item_sku: str, quantity: int, timestamp: str
    ) -> None:
        """Log a warehouse transaction."""
        tx = WarehouseTransaction(
            tx_id=tx_id,
            warehouse_name=self.warehouse.name,
            tx_type=tx_type,
            item_sku=item_sku,
            quantity=quantity,
            timestamp=timestamp,
        )
        self.transaction_log.append(tx)
