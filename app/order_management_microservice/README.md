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


## Access the microservice at
https://order_management-1-w1405204.deta.app/


## Access the API documentation at
https://order_management-1-w1405204.deta.app/docs




