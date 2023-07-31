# Order Management Microservice

This microservice manages the processing of customer orders.

## API Documentation

#### GET /orders: 
Get all orders.


##### Response

`200 OK`: Successful operation. Returns a list of orders.


```
@app.get("/orders")
def get_all_orders():
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    if not orders:
        return {"message": "No orders were found.", "orders": []}
    return {"orders": orders}
```



#### GET /orders/{customer_id}:
Fetch all orders for the specified customer.


##### Parameters

`customer_id`: ID of the customer for whom to retrieve the orders.

##### Response

`200 OK`: Successful operation. Returns a list of orders.

`404 Not Found`: No orders found for the specified customer.


```
@app.get("/orders/{customer_id}")
def get_orders(customer_id: int):
    cur.execute("SELECT * FROM orders WHERE customer_id = %s", (customer_id,))
    orders = cur.fetchall()
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Orders for customer with id: {customer_id} were not found")
    return {"orders": orders}
```



#### GET /orders/{order_id}: 
Returns the order with the specified ID.


##### Parameters

`order_id`: ID of the order to retrieve.

##### Response

`200 OK`: Successful operation. Returns the order with the specified ID.

`404 Not Found`: Order with the specified ID not found.


```
@app.get("/orders")
def get_all_orders():
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    if not orders:
        return {"message": "No orders were found.", "orders": []}
    return {"orders": orders}
```



#### POST /orders/{customer_id}:
Creates a new order for the specified customer.

##### Parameters

`customer_id`: ID of the customer for whom the order is to be created.

##### Request Body

`items (array of objects)`: Array of order items.

`product_id (integer)`: ID of the product.

`quantity (integer)`: Quantity of the product.

##### Response

`201 Created`: Order created successfully.

`400 Bad Request`:  Insufficient inventory for one or more items.

`500 Internal Server Error`: Failed to create the order.



```
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
```



## Dependencies
This service is dependent on two other services:

`Product Catalog Service`: This service is used to retrieve product details and update inventory levels when an order is placed. The order management service makes GET and PUT requests to this service.

`Shopping Cart Service`: This service is used to retrieve the customer's shopping cart when placing an order. The order management service makes GET and PUT requests to this service.


```
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


```

## Database Connection
This service uses `PostgreSQL` as its database which is deployed on `Amazon RDS`. It connects to the PostgreSQL instance using the psycopg2 library. The database connection parameters are specified within the application code, including the database name, user, password, host, and port.

Upon application start-up, the service automatically connects to the database using the provided credentials and host information. The code then checks for the existence of necessary tables (orders and order_items) and creates them if they do not exist.


```
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
```



### Database Tables
There are two tables created within this service:

#### orders: This table keeps track of all customer orders. It has three fields:

`id`: A unique identifier for the order.

`customer_id`: The identifier for the customer who placed the order.

`status`: The status of the order (e.g., 'Ordered').


#### order_items: This table stores details of all items in each order. It has four fields:

`id`: A unique identifier for the order item.

`product_id`: The identifier for the product ordered.

`quantity`: The number of units of the product ordered.

`order_id`: The identifier of the order in which the item was ordered. This is a foreign key referencing the id field in the orders table.


```
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
```


```
class OrderItem(BaseModel):
    product_id: int
    quantity: int


class Order(BaseModel):
    id: int
    customer_id: int
    items: list[OrderItem]
    status: str
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



## Access the microservice at
https://order_management-1-w1405204.deta.app/

Refer to the API documentation for detailed information on request/response payloads and usage.

## Access the API documentation at Swagger UI
https://order_management-1-w1405204.deta.app/docs

## Access the Postman API Test Collection:
app/Postman API Test Collection




