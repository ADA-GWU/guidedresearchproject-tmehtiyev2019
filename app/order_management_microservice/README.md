# Order Management Microservice

This microservice manages the processing of customer orders.

## API Documentation

API Documentation
GET /orders: 
Get all orders.

GET /orders/{order_id}: 
Get order by ID.

POST /orders: 
Create a new order.

PUT /orders/{order_id}: 
Update order status by ID.

GET /orders:
Returns a list of all orders.

Response

200 OK: Successful operation. Returns a list of orders.
GET /orders/{order_id}
Returns the order with the specified ID.

Parameters

order_id: ID of the order to retrieve.
Response

200 OK: Successful operation. Returns the order with the specified ID.
404 Not Found: Order with the specified ID not found.
POST /orders
Creates a new order.

Request Body

id (integer): ID of the order.
customer_name (string): Name of the customer.
items (array of objects): Array of order items.
product_id (integer): ID of the product.
quantity (integer): Quantity of the product.
Response

201 Created: Order created successfully.
500 Internal Server Error: Failed to create the order.
PUT /orders/{order_id}
Updates the status of the order with the specified ID.

Parameters

order_id: ID of the order to update.
Request Body

status (string): New status of the order.
Response

200 OK: Successful operation. Order status updated successfully.
404 Not Found: Order with the specified ID not found.


## Access the microservice at
http://localhost:8003

## How to Run

1. Install Docker on your machine.

2. Build the Docker image:
   ```bash
   docker build -t order-management-microservice .