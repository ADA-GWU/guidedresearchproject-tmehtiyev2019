from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.responses import Response
import psycopg2
from psycopg2.extras import RealDictCursor
import requests


try:
    conn = psycopg2.connect(
        dbname='shopping_cart_db',
        user='postgres',
        password="qwer1234!",
        host='database-1.cyxnkg8bocgc.us-east-2.rds.amazonaws.com',
        port="5432",
        cursor_factory=RealDictCursor
    )
except psycopg2.Error as e:
    print("Unable to connect to the database")

try:
    cur = conn.cursor()

    # Create a 'carts' table
    create_carts_table_query = '''
    CREATE TABLE IF NOT EXISTS carts(
        id SERIAL PRIMARY KEY,
        customer_id INT NOT NULL,
        status VARCHAR NOT NULL
    )
    '''

    # Create a 'cart_items' table
    create_cart_items_table_query = '''
    CREATE TABLE IF NOT EXISTS cart_items(
        id SERIAL PRIMARY KEY,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        cart_id INT,
        FOREIGN KEY (cart_id) REFERENCES carts (id)
    )
    '''

    cur.execute(create_carts_table_query)
    cur.execute(create_cart_items_table_query)

    conn.commit()
    print("Tables created successfully")

except psycopg2.Error as e:
    print("An error occurred while creating the tables:", e)



class CartItem(BaseModel):
    product_id: int
    quantity: int


class Cart(BaseModel):
    id: int
    customer_id: int
    status: str
    items: list[CartItem]


app = FastAPI()

@app.get("/")
def root():
    return {"message":"Welcome to shopping cart service."}

@app.get("/carts")
def get_all_carts():
    cur.execute("SELECT * FROM carts")
    all_carts = cur.fetchall()
    if not all_carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="No carts found")
    return {"carts": all_carts}

@app.get("/cart_items")
def get_all_cart_items():
    cur.execute("SELECT * FROM cart_items")
    items = cur.fetchall()
    if items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="No items found in any cart")
    return {"items": items}

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
    response = requests.get(f"http://product_catalog-1-f3543029.deta.app/products/{cart_item.product_id}",verify=False)
    if response.status_code == 200:
        product = response.json()["product_detail"]
        if product['quantity'] >= cart_item.quantity:
            cur.execute("SELECT id FROM carts WHERE customer_id = %s AND status = 'Active'", (customer_id,))
            cart = cur.fetchone()
            if cart is None:
                cur.execute("INSERT INTO carts (customer_id, status) VALUES (%s, 'Active') RETURNING id", 
                            (customer_id,))
                cart_id = cur.fetchone()["id"]
            else:
                cart_id = cart["id"]
            cur.execute("INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s)",
                        (cart_id, cart_item.product_id, cart_item.quantity))
            conn.commit()
            return {"message": "Item added to cart successfully"}
        else:
            return f"Not enough product in stock"
            # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
            #                     detail="Not enough product in stock")
    else:
        return f"Product with id {cart_item.product_id} not found"
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        #                     detail=f"Product with id {cart_item.product_id} not found")


@app.delete("/carts/{customer_id}/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_from_cart(customer_id: int, product_id: int):
    cur.execute("DELETE FROM cart_items WHERE cart_id IN (SELECT id FROM carts WHERE customer_id = %s and status = 'Active') AND product_id = %s",
                (customer_id, product_id))
    conn.commit()
    if cur.rowcount == 0:
        return f"product with id: {product_id} does not exist in the cart of customer with id: {customer_id}"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"product with id: {product_id} does not exist in the cart of customer with id: {customer_id}")
    return {"message": f"The product id {product_id} with customer id {customer_id} was deleted from the cart items"}



@app.put("/carts/{customer_id}/{product_id}")
def update_item_in_cart(customer_id: int, product_id: int, updated_cart_item: CartItem):
    response = requests.get(f"https://product_catalog-1-f3543029.deta.app/products/{product_id}",verify=False)
    if response.status_code == 200:
        product = response.json()["product_detail"]
        if product['quantity'] >= updated_cart_item.quantity:
            cur.execute("UPDATE cart_items SET quantity = %s WHERE cart_id IN (SELECT id FROM carts WHERE customer_id = %s AND status = 'Active') AND product_id = %s",
                        (updated_cart_item.quantity, customer_id, product_id))
            conn.commit()
            if cur.rowcount == 0:
                return f"Product with id: {product_id} does not exist in the cart of customer with id: {customer_id}"
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail=f"Product with id: {product_id} does not exist in the cart of customer with id: {customer_id}")
            return {"message": "Item quantity updated successfully"}
        else:
            return "Not enough product in stock"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Not enough product in stock")
    else:
        return f"Product with id {product_id} not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Product with id {product_id} not found")


@app.put("/carts/{customer_id}", status_code=status.HTTP_200_OK)
def update_cart_status(customer_id: int, status: str = 'Ordered'):
    cur.execute("UPDATE carts SET status = %s WHERE customer_id = %s AND status = 'Active'", (status, customer_id))
    conn.commit()
    if cur.rowcount == 0:
        return {"message": "Cart status updated successfully"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No active cart found for customer with id: {customer_id}")
    return {"message": "Cart status updated successfully"}
