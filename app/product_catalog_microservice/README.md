# Product Catalog Microservice

This microservice is responsible for managing the product inventory, details, and availability.


## API Documentation
#### GET /products:

Get all products.

#### Response
`200 OK`: Successful operation. Returns a list of products.

#### GET /products/{product_id}:

Returns the product with the specified ID.

#### Parameters
`product_id`: ID of the product to retrieve.

#### Response
`200 OK`: Successful operation. Returns the product with the specified ID.

`404 Not Found`: Product with the specified ID not found.

#### POST /products:
Creates a new product in the catalog.

#### Request Body
name (string): Name of the product.

`price (integer)`: Price of the product.

`quantity (integer)`: Quantity of the product in the inventory.

#### Response

`201 Created`: Product created successfully.

`500 Internal Server Error`: Failed to create the product.

#### PUT /products/{product_id}:
Updates the specified product in the catalog.

#### Parameters
product_id: ID of the product to update.

#### Request Body
`name (string)`: New name of the product.

`price (integer)`: New price of the product.

`quantity (integer)`: New quantity of the product in the inventory.

#### Response
`200 OK`: Successful operation. Product updated successfully.

`404 Not Found`: Product with the specified ID not found.

#### DELETE /products/{product_id}:
Deletes the specified product from the catalog.

#### Parameters
product_id: ID of the product to delete.

#### Response
`204 No Content`: Product deleted successfully.

`404 Not Found`: Product with the specified ID not found.

## Dependencies

This service is independent and does not have any dependencies.

## Database Connection

This service uses PostgreSQL as its database which is deployed on Amazon RDS. It connects to the PostgreSQL instance using the psycopg2 library. The database connection parameters are specified within the application code, including the database name, user, password, host, and port.

Upon application start-up, the service automatically connects to the database using the provided credentials and host information. The code then checks for the existence of necessary tables (products) and creates them if they do not exist.

### Database Tables
There is one table created within this service:

#### products: This table stores the details of all products in the catalog. It has four fields:
`id` : A unique identifier for the product.

`name`: The name of the product.

`price`: The price of the product.

`quantity`: The quantity of the product in the inventory.

## Service Deployment
This service is designed to be deployed to Deta Space, a cloud-based, scalable environment for running FastAPI applications. The deployment process is similar to the Order Management Service.

## Access the microservice at
https://product_catalog-1-w1405204.deta.app/

Refer to the API documentation for detailed information on request/response payloads and usage.

## Access the API documentation at
https://product_catalog-1-w1405204.deta.app/docs


