from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import time

# Connect to the database
try:
    conn = psycopg2.connect(
        dbname='order_management_db',
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

    # Create 'orders' table
    create_orders_table_query = '''
    CREATE TABLE IF NOT EXISTS orders(
        id SERIAL PRIMARY KEY,
        customer_id INT NOT NULL,
        status VARCHAR NOT NULL
    )
    '''

    # Create 'order_items' table
    create_order_items_table_query = '''
    CREATE TABLE IF NOT EXISTS order_items(
        id SERIAL PRIMARY KEY,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        order_id INT,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )
    '''

    cur.execute(create_orders_table_query)
    cur.execute(create_order_items_table_query)

    conn.commit()
    print("Tables created successfully")

except psycopg2.Error as e:
    print("An error occurred while creating the tables:", e)


class OrderItem(BaseModel):
    product_id: int
    quantity: int


class Order(BaseModel):
    id: int
    customer_id: int
    items: list[OrderItem]
    status: str


app = FastAPI()

@app.get("/")
def root():
    return {"message":"Welcome to order management service."}

@app.post("/orders/{customer_id}")
def create_order(customer_id: int):
    # Retrieve the customer's shopping cart from the Shopping Cart Microservice
    response = requests.get(f"https://product_catalog-1-f3543029.deta.app/carts/{customer_id}")
    if response.status_code == 200:
        cart = response.json()

        # Confirm that sufficient inventory is available for each item in the cart
        for item in cart['items']:
            product = requests.get(f"https://product_catalog-1-f3543029.deta.app/products/{item['product_id']}").json()
            if product['quantity'] < item['quantity']:
                return {"message": f"Not enough product in stock for product id {item['product_id']}"}, 400

        # If we reach here, it means we have enough inventory for all items in the cart.
        # Now, decrease the product quantity in the Product Catalog Service and create the order
        cur.execute("INSERT INTO orders (customer_id, status) VALUES (%s, 'Ordered') RETURNING id",
                    (customer_id,))
        order_id = cur.fetchone()['id']
        for item in cart['items']:
            product = requests.get(f"https://product_catalog-1-f3543029.deta.app/products/{item['product_id']}").json()
            product['quantity'] -= item['quantity']
            requests.put(f"https://product_catalog-1-f3543029.deta.app/products/{item['product_id']}", json=product)

            cur.execute("INSERT INTO order_items (product_id, quantity, order_id) VALUES (%s, %s, %s)",
                        (item['product_id'], item['quantity'], order_id))
        conn.commit()

        # Updating the order status in the Shopping Cart Microservice
        response = requests.put(f"https://product_catalog-1-f3543029.deta.app/carts/{customer_id}", json={"status": "Ordered"})
        if response.status_code != 200:
            return {"message": "Failed to update cart status"}, 500

        return {"message": "Order created successfully"}, 201

    return {"message": "Failed to retrieve the customer's shopping cart"}, 500


@app.get("/orders")
def get_all_orders():
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    if not orders:
        return {"message": "No orders were found.", "orders": []}
    return {"orders": orders}


@app.get("/orders/{customer_id}")
def get_orders(customer_id: int):
    cur.execute("SELECT * FROM orders WHERE customer_id = %s", (customer_id,))
    orders = cur.fetchall()
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Orders for customer with id: {customer_id} were not found")
    return {"orders": orders}
