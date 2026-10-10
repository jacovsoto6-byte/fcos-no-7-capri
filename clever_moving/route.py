"""Route optimization for clever_moving.

Computes optimal routes based on distance, cost, risk, and time constraints.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

from .core import Address, FreightPlan


@dataclass
class RouteOption:
    name: str
    mode: str
    estimated_days: int
    cost: float
    risk_level: str
    distance_miles: float
    score: float  # Composite optimization score


class RouteOptimizer:
    """Computes optimal shipping routes."""

    # Simplified city coordinates (lat, lon)
    CITY_COORDS = {
        "Dallas": (32.7767, -96.7970),
        "Denver": (39.7392, -104.9903),
        "Austin": (30.2672, -97.7431),
        "Houston": (29.7604, -95.3698),
        "Phoenix": (33.4484, -112.0742),
        "Los Angeles": (34.0522, -118.2437),
        "San Francisco": (37.7749, -122.4194),
        "Seattle": (47.6062, -122.3321),
        "New York": (40.7128, -74.0060),
        "Boston": (42.3601, -71.0589),
    }

    @staticmethod
    def _haversine_distance(city1: str, city2: str) -> float:
        """Calculate distance between two cities in miles."""
        if city1 not in RouteOptimizer.CITY_COORDS or city2 not in RouteOptimizer.CITY_COORDS:
            return 500.0  # Default estimate

        lat1, lon1 = RouteOptimizer.CITY_COORDS[city1]
        lat2, lon2 = RouteOptimizer.CITY_COORDS[city2]

        R = 3959  # Earth radius in miles
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    @staticmethod
    def generate_options(origin: Address, destination: Address) -> List[RouteOption]:
        """Generate multiple route options."""
        distance = RouteOptimizer._haversine_distance(origin.city, destination.city)

        truck_days = max(2, int(distance / 500))
        rail_days = max(3, int(distance / 400))
        air_days = max(1, int(distance / 2000))
        ocean_days = max(7, int(distance / 300))

        truck_cost = distance * 3.5
        rail_cost = distance * 1.8
        air_cost = distance * 8.0
        ocean_cost = distance * 0.9

        options = [
            RouteOption(
                name="Standard Truck Route",
                mode="truck",
                estimated_days=truck_days,
                cost=truck_cost,
                risk_level="low",
                distance_miles=distance,
                score=0.0,
            ),
            RouteOption(
                name="Rail Express",
                mode="rail",
                estimated_days=rail_days,
                cost=rail_cost,
                risk_level="low",
                distance_miles=distance,
                score=0.0,
            ),
            RouteOption(
                name="Air Freight Priority",
                mode="air",
                estimated_days=air_days,
                cost=air_cost,
                risk_level="medium",
                distance_miles=distance,
                score=0.0,
            ),
            RouteOption(
                name="Ocean Freight Economy",
                mode="ocean",
                estimated_days=ocean_days,
                cost=ocean_cost,
                risk_level="medium",
                distance_miles=distance,
                score=0.0,
            ),
        ]

        for option in options:
            option.score = RouteOptimizer._compute_score(option)

        return sorted(options, key=lambda o: o.score, reverse=True)

    @staticmethod
    def _compute_score(option: RouteOption) -> float:
        """Composite score: balance cost, speed, and risk."""
        cost_factor = 1.0 / max(option.cost, 1.0)
        speed_factor = 1.0 / max(option.estimated_days, 1.0)
        risk_factor = {"low": 1.0, "medium": 0.8, "high": 0.5}.get(option.risk_level, 0.5)
        return (cost_factor * 0.4 + speed_factor * 0.4 + risk_factor * 0.2) * 100
