# clever_moving

A compact logistics and manufacturing coordination package.

## Features

- Moving and route planning
- Freight scheduling
- Warehouse capacity checks
- Vehicle inspection gating
- Manufacturing urgency prioritization

## Example

```bash
python -m clever_moving.cli --origin-city Dallas --dest-city Denver --mode truck --priority high
```

## Python usage

```python
from clever_moving import Address, FreightPlan, Warehouse, VehicleInspection, ManufacturingOrder, optimize_plan

warehouse = Warehouse(
    name="North Hub",
    location=Address(city="Austin", state="TX", zip_code="78701", country="US"),
    capacity_units=120,
    available_units=40,
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

order = ManufacturingOrder(
    order_id="MFG-1001",
    item="control panel kit",
    units=150,
    needed_by="2026-10-20",
    priority="high",
    warehouse_name="North Hub",
)

plan = optimize_plan(freight, warehouse, inspection, order)
print(plan.recommended_action)
```
