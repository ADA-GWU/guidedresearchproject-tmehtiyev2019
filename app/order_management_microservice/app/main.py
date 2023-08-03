from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.responses import Response
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import time
from typing import List

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


@app.post("/orders/{customer_id}", status_code=status.HTTP_201_CREATED)
def create_order(customer_id: int):
    # Retrieve the customer's shopping cart from the Shopping Cart Microservice
    try:
        response_cart = requests.get(f"https://shopping_cart-1-y6546994.deta.app/carts/{customer_id}",verify=False)
    except requests.exceptions.RequestException as e:
        # This will catch any type of RequestException, including ConnectionError, Timeout, TooManyRedirects, etc.
        # You can handle the exception here, e.g., by logging it, retrying the request, returning a response indicating an error, etc.
        print(f"An error occurred while trying to get the cart: {e}")

    
    
    if response_cart.status_code == 200:
        cart = response_cart.json()
        cart_id = cart['cart']['id']
        


        # Now we get the cart items
        response_items = requests.get(f"https://shopping_cart-1-y6546994.deta.app/cart_items",verify=False)
        
        if response_items.status_code == 200:
            items = response_items.json()

            if len([item for item in items['items'] if item['cart_id'] == cart_id])==0:
                return{"message": "There is no selected card item for the customer"},500
            
        
            # Confirm that sufficient inventory is available for each item in the cart
            for item in [item for item in items['items'] if item['cart_id'] == cart_id]:
             
                # Get inventory data for item
                
                response_inventory = requests.get(f"https://product_catalog-1-f3543029.deta.app/products/{item['product_id']}",verify=False)
            
                if response_inventory.status_code != 200:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item: {item['product_id']} not found in the stock")
                inventory_item = response_inventory.json()
                
                # Check inventory availability
                if inventory_item['product_detail']['quantity'] < item['quantity']:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not enough quantity for item: {item['product_id']} in the stock")
                

                    # If we reach here, it means we have enough inventory for all items in the cart.
            # Now, decrease the product quantity in the Product Catalog Service and create the order
            cur.execute("INSERT INTO orders (customer_id, status) VALUES (%s, 'Ordered') RETURNING id",
                        (customer_id,))
            
            order_id = cur.fetchone()['id']
            
            for item in [item for item in items['items'] if item['cart_id'] == cart_id]:
                product = requests.get(f"https://product_catalog-1-f3543029.deta.app/products/{item['product_id']}",verify=False).json()
                product['product_detail']['quantity'] -= item['quantity']
                
                requests.put(f"https://product_catalog-1-f3543029.deta.app/products/{item['product_id']}",verify=False, json=product['product_detail'])
                

                cur.execute("INSERT INTO order_items (product_id, quantity, order_id) VALUES (%s, %s, %s)",
                            (item['product_id'], item['quantity'], order_id))
                
            conn.commit()

        

                    # Updating the order status in the Shopping Cart Microservice
            response = requests.put(f"https://shopping_cart-1-y6546994.deta.app/carts/{customer_id}",verify=False, json={"status": "Ordered"})
            
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


@app.get("/order_items")
def get_all_order_items():
    cur.execute("SELECT * FROM order_items")
    items = cur.fetchall()
    if items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="No items found in any cart")
    return {"items": items}
