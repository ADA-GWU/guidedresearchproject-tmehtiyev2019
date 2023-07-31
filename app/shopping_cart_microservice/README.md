# Shopping Cart Microservice

This microservice handles the management of customer shopping carts.


## API Documentation
#### GET /carts:

Get all shopping carts.

#### Response:

`200 OK`: Successful operation. Returns a list of shopping carts.
`404 Not` Found: No shopping carts found.


```
@app.get("/carts")
def get_all_carts():
    cur.execute("SELECT * FROM carts")
    all_carts = cur.fetchall()
    if not all_carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="No carts found")
    return {"carts": all_carts}
```


#### GET /cart_items:
Get all items in all shopping carts.

#### Response:

`200 OK`: Successful operation. Returns a list of all items in all shopping carts.
`404 Not Found`: No items found in any shopping cart.


```
@app.get("/cart_items")
def get_all_cart_items():
    cur.execute("SELECT * FROM cart_items")
    items = cur.fetchall()
    if items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="No items found in any cart")
    return {"items": items}
```


#### GET /carts/{customer_id}:

Returns the active cart for the customer with the specified ID.

#### Parameters:

`customer_id`: ID of the customer whose cart is to be retrieved.

#### Response:

`200 OK`: Successful operation. Returns the active cart of the customer with the specified ID.
`404 Not Found`: No active cart found for the customer with the specified ID.


```
@app.get("/carts/{customer_id}")
def get_cart(customer_id: int):
    cur.execute("SELECT * FROM carts WHERE customer_id = %s AND status = 'Active'", (customer_id,))
    cart = cur.fetchone()
    if cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Active cart for customer with id: {customer_id} was not found")
    return {"cart": cart}
```


#### POST /carts/{customer_id}:
Adds an item to the active cart of the customer with the specified ID.

#### Parameters:

`customer_id`: ID of the customer whose cart the item is to be added to.

#### Request Body:

`product_id (integer)`: ID of the product to be added.
`quantity (integer)`: Quantity of the product to be added.


#### Response:

`201 Created`: Item added successfully to the cart.
`400 Bad Request`: Not enough product in stock.
`404 Not Found`: Product with the specified ID not found.


```
@app.post("/carts/{customer_id}", status_code=status.HTTP_201_CREATED)
def add_item_to_cart(customer_id: int, cart_item: CartItem):
    response = requests.get(f"https://product_catalog-1-f3543029.deta.app/products/{cart_item.product_id}")
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Not enough product in stock")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Product with id {cart_item.product_id} not found")

```


#### DELETE /carts/{customer_id}/{product_id}:

Deletes the specified product from the cart of the customer with the specified ID.

#### Parameters:

`customer_id`: ID of the customer whose cart the item is to be deleted from.
`product_id`: ID of the product to be deleted.

#### Response:

`204 No Content`: Product deleted successfully from the cart.
`404 Not Found`: Product with the specified ID not found in the cart of the customer with the specified ID.


```
@app.delete("/carts/{customer_id}/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_from_cart(customer_id: int, product_id: int):
    cur.execute("DELETE FROM cart_items WHERE cart_id IN (SELECT id FROM carts WHERE customer_id = %s) AND product_id = %s",
                (customer_id, product_id))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"product with id: {product_id} does not exist in the cart of customer with id: {customer_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```


#### PUT /carts/{customer_id}/{product_id}:
Updates the quantity of a specific item in the active cart of the customer with the specified ID.

#### Parameters:

`customer_id`: ID of the customer whose cart the item is in.
`product_id`: ID of the product whose quantity is to be updated.

#### Request Body:

`quantity (integer)`: New quantity of the product in the cart.

#### Response:

`200 OK`: Successful operation. Item quantity updated successfully.
`400 Bad Request`: Not enough product in stock.
`404 Not Found`: Product with the specified ID not found in the cart of the customer with the specified ID.


```
@app.put("/carts/{customer_id}/{product_id}")
def update_item_in_cart(customer_id: int, product_id: int, updated_cart_item: CartItem):
    response = requests.get(f"https://product_catalog-1-f3543029.deta.app/products/{product_id}")
    if response.status_code == 200:
        product = response.json()["product_detail"]
        if product['quantity'] >= updated_cart_item.quantity:
            cur.execute("UPDATE cart_items SET quantity = %s WHERE cart_id IN (SELECT id FROM carts WHERE customer_id = %s AND status = 'Active') AND product_id = %s",
                        (updated_cart_item.quantity, customer_id, product_id))
            conn.commit()
            if cur.rowcount == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail=f"Product with id: {product_id} does not exist in the cart of customer with id: {customer_id}")
            return {"message": "Item quantity updated successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Not enough product in stock")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Product with id {product_id} not found")

```

#### PUT /carts/{customer_id}:
Updates the status of the active cart of the customer with the specified ID.

#### Parameters:

`customer_id`: ID of the customer whose cart status is to be updated.

#### Request Body:

`status (string)`: New status of the cart ('Ordered' by default).

#### Response:

`202 Accepted`: Cart status updated successfully.
`404 Not Found`: No active cart found for the customer with the specified ID.


```
@app.put("/carts/{customer_id}", status_code=status.HTTP_202_ACCEPTED)
def update_cart_status(customer_id: int, status: str = 'Ordered'):
    cur.execute("UPDATE carts SET status = %s WHERE customer_id = %s AND status = 'Active'", (status, customer_id))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No active cart found for customer with id: {customer_id}")
    return {"message": "Cart status updated successfully"}
```

## Dependencies
This service is dependent on the Product Catalog Microservice for product data.

* The Shopping Cart Microservice is dependent on the `Product Catalog Microservice` for information about the products. Here's what this dependency involves:

When a customer wants to add a product to their shopping cart, the Shopping Cart Microservice needs to check the Product Catalog Microservice to ensure the product exists and to get its details. This means there is a call from the Shopping Cart Microservice to the Product Catalog Microservice.


```
@app.post("/carts/{customer_id}", status_code=status.HTTP_201_CREATED)
def add_item_to_cart(customer_id: int, cart_item: CartItem):
    response = requests.get(f"https://product_catalog-1-f3543029.deta.app/products/{cart_item.product_id}")
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Not enough product in stock")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Product with id {cart_item.product_id} not found")

```

Similarly, when a customer updates the quantity of a product in their cart, the Shopping Cart Microservice has to ensure that enough quantity of the product is available. This information is retrieved from the Product Catalog Microservice.


```
@app.put("/carts/{customer_id}/{product_id}")
def update_item_in_cart(customer_id: int, product_id: int, updated_cart_item: CartItem):
    response = requests.get(f"https://product_catalog-1-f3543029.deta.app/products/{product_id}")
    if response.status_code == 200:
        product = response.json()["product_detail"]
        if product['quantity'] >= updated_cart_item.quantity:
            cur.execute("UPDATE cart_items SET quantity = %s WHERE cart_id IN (SELECT id FROM carts WHERE customer_id = %s AND status = 'Active') AND product_id = %s",
                        (updated_cart_item.quantity, customer_id, product_id))
            conn.commit()
            if cur.rowcount == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                    detail=f"Product with id: {product_id} does not exist in the cart of customer with id: {customer_id}")
            return {"message": "Item quantity updated successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Not enough product in stock")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Product with id {product_id} not found")

```

These dependencies are managed through API calls between the two services as described in the codes above.

## Database Connection
This service uses PostgreSQL as its database which is deployed on Amazon RDS. It connects to the PostgreSQL instance using the psycopg2 library. The database connection parameters are specified within the application code, including the database name, user, password, host, and port.

Upon application start-up, the service automatically connects to the database using the provided credentials and host information. The code then checks for the existence of necessary tables (carts and cart_items) and creates them if they do not exist.


```
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

```

### Database Tables
There are two tables created within this service:

#### carts: This table stores the details of all shopping carts. It has three fields:

`id`: A unique identifier for the shopping cart.
`customer_id`: The ID of the customer who owns the cart.
`status`: The status of the shopping cart.

#### cart_items: This table stores the details of all items in all shopping carts. It has four fields:

`id`: A unique identifier for the item.
`product_id`: The ID of the product.
`quantity`: The quantity of the product in the cart.
`cart_id`: The ID of the cart that the item is in.


```
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
```


## Service Deployment

This service is designed to be deployed to `Deta Space`, a cloud-based, scalable environment for running FastAPI applications. Here are step-by-step instructions on how to do this:

### Create a FastAPI App

* Create a new directory for your app:


```

mkdir fastapi-deta
cd fastapi-deta

```

* Create a `main.py` file with your FastAPI code.

* Create a `requirements.txt` file with the following content:


```
fastapi
uvicorn[standard]
```



### Set up Deta Space

* Create a free Deta Space account. Developer Mode should be enabled when you sign up.

* Install the Deta Space CLI:


```
curl -fsSL https://get.deta.dev/space-cli.sh | sh
```

Restart your terminal after installing.

* Install the Deta Space CLI: Generate an access token from your Deta Space Canvas settings and use it to login:


```
space login
```

* Create a new project in Space:


  ```
  space new
  ```

You will be prompted for your project's name, let's say `fastapi-deta`. The CLI will automatically detect the framework or language you are using and create a new Space Project.

* Define the run command in the Spacefile: Add the command `uvicorn main:app` under the `run` key in your Spacefile.

* Deploy to Deta Space:

  
```
space push
```

This command will package your code, upload all the necessary files to Deta Space, and run a remote build of your app.

* Enable public access: If you want to make your API public, add the `public_routes` parameter to your Spacefile: 


```
v: 0
micros:
  - name: fastapi-deta
    src: .
    engine: python3.9
    public_routes:
      - "/*"
```

Run `space push` again to update your live API on Deta Space.

* Create a release:If you want to publish your API, run `space release` in the Space CLI to create an unlisted release. If you want your app to be publicly discoverable, create a listed release with `space release --listed`.
  
* Check runtime logs: You can add logging functionality to your app by adding print statements to your code. You can then view your app's logs in your Deta Space's Canvas.

Note that Deta Space takes care of HTTPS, running on startup, restarts, replication, authentication, and memory limits for you. More complex deployment processes can be configured using the Spacefile. You can read more in the Deta Space Documentation.


## Software Dependencies
The Shopping Cart Microservice is dependent on several software libraries for its operation:

### FastAPI: This is the web framework used to build the API of the Shopping Cart Microservice. FastAPI is modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

### psycopg2: This is a PostgreSQL database adapter for Python. The Shopping Cart Microservice uses this library to connect to its PostgreSQL database that is hosted on Amazon RDS.

### Requests: This is a Python library used for making HTTP requests. It abstracts the complexities of making requests behind a simple API, allowing you to send HTTP/1.1 requests. The Shopping Cart Microservice uses this library to communicate with the Product Catalog Microservice.

These dependencies are listed in a requirements.txt file and installed in the environment where the service runs using pip, the Python package installer.

## Access the microservice at
https://shopping_cart-1-y6546994.deta.app/

Refer to the API documentation for detailed information on request/response payloads and usage.

## Access the API documentation at Swagger UI
https://shopping_cart-1-y6546994.deta.app/docs

## Access the Postman API Test Collection:
app/Postman API Test Collection