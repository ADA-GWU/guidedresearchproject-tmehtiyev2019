from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

# Mock database
carts = []


class CartItem(BaseModel):
    product_id: int
    quantity: int


@app.get("/carts")
def get_carts():
    return carts


@app.post("/carts")
def create_cart(cart_items: list[CartItem]):
    cart = [item.dict() for item in cart_items]
    carts.append(cart)
    return {"message": "Cart created successfully"}, 201


@app.put("/carts/{cart_id}")
def update_cart(cart_id: int, cart_items: list[CartItem]):
    for cart in carts:
        if cart_id == carts.index(cart):
            cart.clear()
            cart.extend([item.dict() for item in cart_items])
            return {"message": f"Cart with ID: {cart_id} updated successfully"}
    return {"message": "Cart not found"}, 404


@app.delete("/carts/{cart_id}")
def delete_cart(cart_id: int):
    for cart in carts:
        if cart_id == carts.index(cart):
            carts.remove(cart)
            return {"message": f"Cart with ID: {cart_id} deleted successfully"}
    return {"message": "Cart not found"}, 404
