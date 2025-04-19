from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# Product warehouse mapping
warehouse_products = {
    "C1": {"A", "B", "C"},
    "C2": {"D", "E", "F"},
    "C3": {"G", "H", "I"}
}

# Distance/Cost matrix
costs = {
    ("C1", "L1"): 40,
    ("C2", "L1"): 60,
    ("C3", "L1"): 20,
    ("C1", "C2"): 25,
    ("C1", "C3"): 35,
    ("C2", "C3"): 30,
    ("C2", "C1"): 25,
    ("C3", "C1"): 35,
    ("C3", "C2"): 30,
}

class Order(BaseModel):
    A: int = 0
    B: int = 0
    C: int = 0
    D: int = 0
    E: int = 0
    F: int = 0
    G: int = 0
    H: int = 0
    I: int = 0

@app.post("/calculate-cost")
async def calculate_cost(order: Order):
    order_dict = order.dict()
    
    def get_required_warehouses(order):
        warehouses = set()
        for product, qty in order.items():
            if qty > 0:
                for wh, products in warehouse_products.items():
                    if product in products:
                        warehouses.add(wh)
        return warehouses

    min_total_cost = float('inf')

    for start_center in ["C1", "C2", "C3"]:
        if start_center not in get_required_warehouses(order_dict):
            continue

        visited = {start_center}
        to_visit = get_required_warehouses(order_dict) - visited
        route_cost = 0

        # First delivery from starting point
        route_cost += costs[(start_center, "L1")]

        current = start_center
        while to_visit:
            next_stop = to_visit.pop()
            route_cost += costs[(current, next_stop)]  # Pickup
            route_cost += costs[(next_stop, "L1")]     # Deliver to L1
            current = next_stop

        min_total_cost = min(min_total_cost, route_cost)

    return {"cost": min_total_cost}
