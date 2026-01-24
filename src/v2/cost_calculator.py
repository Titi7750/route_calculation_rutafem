from src.v2.models import CostResult


class CostCalculatorV2:


    COMMISSION_RATE = 0.12
    MIN_PRICE_PER_PERSON = 1.99

    VEHICLE_COST_PER_KM = 0.15
    TIME_COST_PER_MIN = 0.0

    def compute_costs(
        self,
        distance_km: float,
        duration_min: float,
        liter_per_100km: float,
        fuel_price_per_liter: float,
        toll_cost: float,
        persons: int,
        commission: bool = True,
    ) -> CostResult:

        if distance_km <= 0:
            raise ValueError("distance_km must be positive")
        if persons <= 0:
            raise ValueError("persons must be >= 1")

       
        fuel_cost = round(
            distance_km * (liter_per_100km / 100) * fuel_price_per_liter,
            2
        )

       
        vehicle_cost = round(
            distance_km * self.VEHICLE_COST_PER_KM,
            2
        )

        
        time_cost = 0.0

        
        subtotal = round(
            fuel_cost + vehicle_cost + time_cost + toll_cost,
            2
        )

        
        if commission:
            total_vehicle_cost = subtotal * (1 + self.COMMISSION_RATE)
        else:
            total_vehicle_cost = subtotal

        total_vehicle_cost = round(total_vehicle_cost, 2)

        
        cost_per_person = round(total_vehicle_cost / persons, 2)

        
        if cost_per_person < self.MIN_PRICE_PER_PERSON:
            cost_per_person = self.MIN_PRICE_PER_PERSON
            total_vehicle_cost = round(cost_per_person * persons, 2)

        return CostResult(
            fuel_cost=fuel_cost,
            vehicle_cost=vehicle_cost,
            time_cost=time_cost,
            toll_cost=round(toll_cost, 2),
            subtotal=subtotal,
            total_vehicle_cost=total_vehicle_cost,
            cost_per_person=cost_per_person,
        )
