from typing import Optional
from fastapi import FastAPI,Response, HTTPException
from fastapi import status
from fastapi.params import Body
from random import randrange
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time


# while True:

try:
    conn = psycopg2.connect(
        dbname='microservicedb',
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

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS products(
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        price INTEGER NOT NULL,
        quantity INTEGER NOT NULL
    )
    '''

    cur.execute(create_table_query)
    conn.commit()
    print("Table created successfully")

except psycopg2.Error as e:
    print("An error occurred while creating the table:", e)

# finally:
#     if cur is not None:
#         cur.close()
#     if conn is not None:
#         conn.close()

app = FastAPI()

class Product(BaseModel):
    name: str
    price: int
    quantity: int


@app.get("/")
def root():
    return {"message":"Welcome to product catalog service."}

@app.get("/products")
def get_products():
    cur.execute("""SELECT * FROM products""")
    products=cur.fetchall()
    # print(products)
    return {"data":products}


@app.get("/products/{product_id}")
def get_product(product_id: int):
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with id: {product_id} was not found")
    return {"product_detail":product}


@app.post("/products", status_code=status.HTTP_201_CREATED )
def add_product(product: Product):
    cur.execute(
        """INSERT INTO products ( name, price, quantity) VALUES (%s, %s, %s) RETURNING * """,
        ( product.name, product.price, product.quantity)
    )
    new_product=cur.fetchone()
    conn.commit()
    return {"data": new_product}

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with id: {product_id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/products/{product_id}")
def update_product(product_id: int, updated_product: Product):
    # check if product exists
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with id: {product_id} was not found")
    
    # update the product
    cur.execute(
        """UPDATE products 
           SET name = %s, price = %s, quantity = %s 
           WHERE id = %s RETURNING *""",
        (updated_product.name, updated_product.price, updated_product.quantity, product_id)
    )
    conn.commit()
    updated_product = cur.fetchone()

    return {"message": "Product updated successfully", "updated_product": updated_product}
