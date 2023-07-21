from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.responses import Response
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import requests


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='ShoppingCart', 
                                user='postgres', password="xxxx", cursor_factory=RealDictCursor)
        cur = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(3)
        break  # temporary

app = FastAPI()


class CartItem(BaseModel):
    product_id: int
    quantity: int


class Cart(BaseModel):
    id: int
    customer_id: int
    items: list[CartItem]
    status: str


@app.get("/carts/{customer_id}")
def get_cart(customer_id: int):
    cur.execute("SELECT * FROM carts WHERE customer_id = %s AND status = 'Active'", (customer_id,))
    cart = cur.fetchone()
    if cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Active cart for customer with id: {customer_id} was not found")
    return {"cart": cart}


@app.post("/carts/{customer_id}", status_code=status.HTTP_201_CREATED)
def add_item_to_cart(customer_id: int, cart_item: CartItem):
    # First, check the quantity of the product in the Product Catalog service
    response = requests.get(f"http://localhost:8000/products/{cart_item.product_id}")
    if response.status_code == 200:
        product = response.json()["product_detail"]
        if product['quantity'] >= cart_item.quantity:
            # If the product has enough quantity, add it to the cart
            cur.execute("INSERT INTO carts (customer_id, product_id, quantity, status) VALUES (%s, %s, %s, 'Active')",
                        (customer_id, cart_item.product_id, cart_item.quantity))
            conn.commit()
            return {"message": "Item added to cart successfully"}
        else:
            # If the product does not have enough quantity, return an error
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Not enough product in stock")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Product with id {cart_item.product_id} not found")


@app.delete("/carts/{customer_id}/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_from_cart(customer_id: int, product_id: int):
    cur.execute("DELETE FROM carts WHERE customer_id = %s AND product_id = %s AND status = 'Active'",
                (customer_id, product_id))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"product with id: {product_id} does not exist in the cart of customer with id: {customer_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/carts/{customer_id}/{product_id}")
def update_item_in_cart(customer_id: int, product_id: int, updated_cart_item: CartItem):
    # First, check the quantity of the product in the Product Catalog service
    response = requests.get(f"http://localhost:8000/products/{product_id}")
    if response.status_code == 200:
        product = response.json()["product_detail"]
        if product['quantity'] >= updated_cart_item.quantity:
            # If the product has enough quantity, update the item in the cart
            cur.execute("UPDATE carts SET quantity = %s WHERE customer_id = %s AND product_id = %s AND status = 'Active'",
                        (updated_cart_item.quantity, customer_id, product_id))
            conn.commit()
            if cur.rowcount == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail=f"Product with id: {product_id} does not exist in the cart of customer with id: {customer_id}")
            return {"message": "Item quantity updated successfully"}
        else:
            # If the product does not have enough quantity, return an error
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Not enough product in stock")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Product with id {product_id} not found")



@app.put("/carts/{customer_id}", status_code=status.HTTP_202_ACCEPTED)
def update_cart_status(customer_id: int, status: str = 'Ordered'):
    cur.execute("UPDATE carts SET status = %s WHERE customer_id = %s AND status = 'Active'", (status, customer_id))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No active cart found for customer with id: {customer_id}")
    return {"message": "Cart status updated successfully"}
