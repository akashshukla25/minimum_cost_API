from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict
from itertools import permutations

app = FastAPI()

# Warehouse product mapping
warehouse_products = {
    "C1": {"A", "B", "C"},
    "C2": {"D", "E", "F"},
    "C3": {"G", "H", "I"}
}

# Cost per trip between locations
delivery_costs = {
    ("C1", "L1"): 10,
    ("C2", "L1"): 20,
    ("C3", "L1"): 30,
    ("C1", "C2"): 15,
    ("C1", "C3"): 25,
    ("C2", "C1"): 15,
    ("C2", "C3"): 10,
    ("C3", "C1"): 25,
    ("C3", "C2"): 10,
    ("L1", "C1"): 10,
    ("L1", "C2"): 20,
    ("L1", "C3"): 30,
}

# Extract which centers are needed for an order
def get_required_centers(order: Dict[str, int]):
    centers = set()
    for product, qty in order.items():
        if qty == 0:
            continue
        for center, items in warehouse_products.items():
            if product in items:
                centers.add(center)
                break
    return centers

# Get total cost for a specific route
def calculate_cost(route):
    cost = 0
    for i in range(len(route) - 1):
        cost += delivery_costs.get((route[i], route[i+1]), float('inf'))
    return cost

# Try all valid routes from each center to fulfill order
def get_minimum_delivery_cost(order: Dict[str, int]):
    required_centers = get_required_centers(order)
    all_centers = ["C1", "C2", "C3"]
    min_cost = float("inf")

    for start in all_centers:
        if start not in required_centers:
            continue
        other_centers = list(required_centers - {start})
        for perm in permutations(other_centers):
            route = [start]
            route_with_l1 = []
            for center in perm:
                route_with_l1 += ["L1", center]
            route_with_l1 += ["L1"]
            final_route = route + route_with_l1
            cost = calculate_cost(final_route)
            if cost < min_cost:
                min_cost = cost

    return min_cost

# Pydantic model for request
class Order(BaseModel):
    __root__: Dict[str, int]

@app.post("/calculate-delivery-cost")
async def calculate_delivery(order: Order):
    order_data = order.__root__
    cost = get_minimum_delivery_cost(order_data)
    return {"minimum_cost": cost}
