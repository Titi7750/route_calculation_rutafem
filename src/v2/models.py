
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class CostResult:
    fuel_cost: float
    vehicle_cost: float
    time_cost: float
    toll_cost: float
    subtotal: float
    total_vehicle_cost: float
    cost_per_person: float


@dataclass
class RouteOption:
    index: int
    distance_km: float
    duration_min: float
    fuel_cost: float
    toll_cost: float
    total_cost: float
    cost_per_person: float
    tags: List[str]
    raw_route: Dict[str, Any]
