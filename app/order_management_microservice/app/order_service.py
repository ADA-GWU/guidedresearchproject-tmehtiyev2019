from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

# Mock database
orders = []


class CartItem(BaseModel):
    product_id: int
    quantity: int


class Order(BaseModel):
    id: int
    customer_name: str
    items: list[CartItem]
    status: str


@app.get("/orders")
def get_orders():
    return orders


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order.id == order_id:
            return order
    return {"message": "Order not found"}, 404


@app.post("/orders")
def create_order(order: Order):
    # Retrieve the customer's shopping cart from the Shopping Cart Microservice
    response = requests.get("http://localhost:8002/carts")
    if response.status_code == 200:
        cart = response.json()

        # Save the order and update inventory in the Product Catalog Microservice
        order.items = cart
        orders.append(order)

        # Make a request to the Product Catalog Microservice to update inventory
        product_ids = [item.product_id for item in cart]
        product_payload = {"product_ids": product_ids}
        response = requests.put("http://localhost:8001/products/update_inventory", json=product_payload)

        if response.status_code == 200:
            # Inventory updated successfully
            return {"message": "Order created successfully"}, 201
        else:
            # Failed to update inventory
            return {"message": "Failed to update inventory"}, 500

    return {"message": "Failed to retrieve the customer's shopping cart"}, 500


@app.put("/orders/{order_id}")
def update_order_status(order_id: int, status: str):
    for order in orders:
        if order.id == order_id:
            order.status = status
            return {"message": f"Order with ID: {order_id} status updated successfully"}
    return {"message": "Order not found"}, 404
