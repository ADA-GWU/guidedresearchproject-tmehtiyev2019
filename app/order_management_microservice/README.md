# Order Management Microservice

This microservice manages the processing of customer orders.

## API Documentation

#### GET /orders: 
Get all orders.


##### Response

`200 OK`: Successful operation. Returns a list of orders.


#### GET /orders/{customer_id}:: 
Fetch all orders for the specified customer.


##### Parameters

`customer_id`: ID of the customer for whom to retrieve the orders.

##### Response

`200 OK`: Successful operation. Returns a list of orders.

`404 Not Found`: No orders found for the specified customer.


#### GET /orders/{order_id}: 
Returns the order with the specified ID.


##### Parameters

`order_id`: ID of the order to retrieve.

##### Response

`200 OK`: Successful operation. Returns the order with the specified ID.

`404 Not Found`: Order with the specified ID not found.

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

#### PUT /orders/{order_id}:
Updates the status of the order with the specified ID.

##### Parameters

`order_id`: ID of the order to update.

##### Request Body

`status (string)`: New status of the order.

##### Response

`200 OK`: Successful operation. Order status updated successfully.

`404 Not Found`: Order with the specified ID not found.

## Dependencies
This service is dependent on two other services:

`Product Catalog Service`: This service is used to retrieve product details and update inventory levels when an order is placed. The order management service makes GET and PUT requests to this service.

`Shopping Cart Service`: This service is used to retrieve the customer's shopping cart when placing an order. The order management service makes GET and PUT requests to this service.

## Database Connection
This service uses `PostgreSQL` as its database which is deployed on `Amazon RDS`. It connects to the PostgreSQL instance using the psycopg2 library. The database connection parameters are specified within the application code, including the database name, user, password, host, and port.

Upon application start-up, the service automatically connects to the database using the provided credentials and host information. The code then checks for the existence of necessary tables (orders and order_items) and creates them if they do not exist.

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

## Access the API documentation at
https://order_management-1-w1405204.deta.app/docs




