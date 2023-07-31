# Shopping Cart Microservice

This microservice handles the management of customer shopping carts.


## API Documentation
#### GET /carts:

Get all shopping carts.

#### Response:

`200 OK`: Successful operation. Returns a list of shopping carts.
`404 Not` Found: No shopping carts found.


#### GET /cart_items:
Get all items in all shopping carts.

#### Response:

`200 OK`: Successful operation. Returns a list of all items in all shopping carts.
`404 Not Found`: No items found in any shopping cart.


#### GET /carts/{customer_id}:

Returns the active cart for the customer with the specified ID.

#### Parameters:

`customer_id`: ID of the customer whose cart is to be retrieved.

#### Response:

`200 OK`: Successful operation. Returns the active cart of the customer with the specified ID.
`404 Not Found`: No active cart found for the customer with the specified ID.


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


#### DELETE /carts/{customer_id}/{product_id}:

Deletes the specified product from the cart of the customer with the specified ID.

#### Parameters:

`customer_id`: ID of the customer whose cart the item is to be deleted from.
`product_id`: ID of the product to be deleted.

#### Response:

`204 No Content`: Product deleted successfully from the cart.
`404 Not Found`: Product with the specified ID not found in the cart of the customer with the specified ID.


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

#### PUT /carts/{customer_id}:
Updates the status of the active cart of the customer with the specified ID.

#### Parameters:

`customer_id`: ID of the customer whose cart status is to be updated.

#### Request Body:

`status (string)`: New status of the cart ('Ordered' by default).

#### Response:

`202 Accepted`: Cart status updated successfully.
`404 Not Found`: No active cart found for the customer with the specified ID.

## Dependencies
This service is dependent on the Product Catalog Microservice for product data.

Database Connection
This service uses PostgreSQL as its database which is deployed on Amazon RDS. It connects to the PostgreSQL instance using the psycopg2 library. The database connection parameters are specified within the application code, including the database name, user, password, host, and port.

Upon application start-up, the service automatically connects to the database using the provided credentials and host information. The code then checks for the existence of necessary tables (carts and cart_items) and creates them if they do not exist.

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
https://shopping_cart-1-y6546994.deta.app/

Refer to the API documentation for detailed information on request/response payloads and usage.

## Access the API documentation at Swagger UI
https://shopping_cart-1-y6546994.deta.app/docs

## Access the Postman API Test Collection:
app/Postman API Test Collection