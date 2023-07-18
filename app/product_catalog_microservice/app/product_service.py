from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Mock database
products = []


class Product(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


@app.get("/products")
def get_products():
    return products


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product.id == product_id:
            return product
    return {"message": "Product not found"}, 404


@app.post("/products")
def add_product(product: Product):
    products.append(product)
    return {"message": "Product added successfully"}, 201


@app.put("/products/{product_id}")
def update_product(product_id: int, updated_product: Product):
    for product in products:
        if product.id == product_id:
            product.name = updated_product.name
            product.price = updated_product.price
            product.quantity = updated_product.quantity
            return {"message": "Product updated successfully"}
    return {"message": "Product not found"}, 404
