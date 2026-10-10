# clever_moving: Full Logistics System

A comprehensive supply chain orchestration platform for:
- Route optimization and shipping coordination
- Warehouse management and capacity planning
- Vehicle fleet inspection and compliance
- Manufacturing order prioritization and scheduling
- Supply chain risk assessment

## Features

✅ **Route Optimization** — Compare truck, rail, air, and ocean routes  
✅ **Warehouse Management** — Track capacity, inventory, and utilization  
✅ **Vehicle Inspection** — Fleet health, defect tracking, compliance gating  
✅ **Manufacturing Scheduler** — Priority-based order scheduling  
✅ **Risk Assessment** — Comprehensive logistics risk scoring  
✅ **Integration** — Full supply chain orchestration  

## Quick Start

### Coordinate a Full Shipment

```bash
python -m clever_moving.cli \
  --command coordinate \
  --order-id ORD-001 \
  --origin-city Dallas \
  --dest-city Denver \
  --units 150 \
  --priority high
```

### Check Fleet Health

```bash
python -m clever_moving.cli --command inspect
```

### Get Warehouse Status

```bash
python -m clever_moving.cli --command warehouse-status
```

### Check Order Status

```bash
python -m clever_moving.cli --command status --order-id ORD-001
```

## Python API

```python
from clever_moving import (
    Address, Warehouse, ManufacturingOrder, VehicleInspection,
    LogisticsCoordinator
)

# Initialize coordinator
coordinator = LogisticsCoordinator()

# Register warehouse
warehouse = Warehouse(
    name="North Hub",
    location=Address(city="Austin", state="TX", zip_code="78701"),
    capacity_units=500,
    available_units=300,
    handling_rate_per_hour=50.0,
)
coordinator.register_warehouse(warehouse)

# Coordinate a shipment
plan = coordinator.coordinate_shipment(
    order_id="ORD-001",
    origin=Address(city="Dallas", state="TX", zip_code="75201"),
    destination=Address(city="Denver", state="CO", zip_code="80202"),
    units=150,
    needed_by="2026-10-25",
    priority="high",
    warehouse_name="North Hub",
    vehicle_id="TRK-204",
    current_mileage=18000.0,
)

print(f"Best Route: {plan.best_route.name}")
print(f"Risk Level: {plan.risk_assessment.overall_risk}")
print(f"Action Items: {plan.action_items}")
```

## System Architecture

### 1. Route Optimization (`route.py`)
- Generates 4 shipping modes: truck, rail, air, ocean
- Calculates distance using Haversine formula
- Computes composite score balancing cost, speed, risk
- Returns ranked options

### 2. Warehouse Management (`warehouse.py`)
- Tracks capacity and inventory
- Allocates and reserves space
- Calculates utilization percentage
- Estimates handling time
- Maintains transaction log

### 3. Fleet Inspection (`fleet.py`)
- Performs vehicle inspections
- Tracks critical/major/minor defects
- Calculates service intervals
- Gates dispatch based on inspection status
- Reports fleet health metrics

### 4. Manufacturing Scheduler (`manufacturing.py`)
- Submits and tracks manufacturing orders
- Prioritizes queue by urgency and priority level
- Estimates manufacturing time
- Manages order status lifecycle
- Tracks backlog

### 5. Risk Assessment (`risk.py`)
- Scores logistics risk (route, cost, time)
- Scores warehouse risk (capacity, handling)
- Scores inspection risk (fleet health, readiness)
- Scores manufacturing risk (priority, timeline)
- Generates mitigation recommendations

### 6. Full Coordination (`coordinator.py`)
- Orchestrates all 5 subsystems
- Creates comprehensive logistics plans
- Assigns warehouses and routes
- Triggers manufacturing and inspection gates
- Generates action items

## Output Example

```
=== Logistics Coordination Plan ===
Order ID: ORD-001
Route: Standard Truck Route (truck)
  Distance: 1,038.3 miles
  ETA: 3 days
  Cost: $3,634.05
  Risk Level: low

Warehouse: North Hub
  Utilization: 42.0%

Manufacturing Status: pending
  Needed by: 2026-10-25

Vehicle Inspection: passed

Risk Assessment
  Overall Risk: medium
  Logistics Risk: 35.2
  Warehouse Risk: 28.1
  Inspection Risk: 0.0
  Manufacturing Risk: 48.3

Action Items:
  1. Assign North Hub for 150 units
  2. Start manufacturing for order ORD-001
  3. Schedule shipment via truck
```

## Configuration

Edit core parameters in each module:

- **Route Optimizer**: City coordinates, mode costs
- **Warehouse**: Capacity, handling rate
- **Fleet Inspector**: Critical defects, service interval
- **Manufacturing Scheduler**: Production rate
- **Risk Assessment**: Risk weights and thresholds

## Integration with Caprise Visor

clever_moving can be integrated as a domain adapter in Caprise Visor:

```python
from caprise.core import Caprise, AMProvider, DCProvider
from clever_moving import LogisticsCoordinator

# Attach logistics coordinator as catalyst action handler
caprise.register_action_handler(
    "logistics_coordinate",
    lambda action: logistics_coordinator.coordinate_shipment(...)
)
```

## Dependencies

- Python 3.9+
- Standard library only (dataclasses, typing, math, datetime)
- No external dependencies

## Next Steps

- [ ] Add database persistence (SQLite/PostgreSQL)
- [ ] Add REST API routes (FastAPI)
- [ ] Add real-time tracking integration
- [ ] Add machine learning demand forecasting
- [ ] Add blockchain settlement records
- [ ] Add multi-warehouse network optimization

## License

Fedora CoreOS Infrastructure Project

## Version

**v0.1.0** — Initial release  
**Date**: 2026-10-10
