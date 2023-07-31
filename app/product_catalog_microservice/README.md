# Product Catalog Microservice

This microservice is responsible for managing the product inventory, details, and availability.

## API Documentation

GET /products
Get all products.

GET /products/{product_id}
Get product by ID.

POST /products
Add a new product.

PUT /products/{product_id}
Update product by ID.

## Dependencies
This service is dependent on two other services:

`Product Catalog Service` : This service is used to retrieve product details and update inventory levels when an order is placed. The order management service makes GET and PUT requests to this service.

`Shopping Cart Service` : This service is used to retrieve the customer's shopping cart when placing an order. The order management service makes GET and PUT requests to this service.


## Access the microservice at
https://product_catalog-1-f3543029.deta.app/

Refer to the API documentation for detailed information on request/response payloads and usage.

## Access the API documentation at
https://product_catalog-1-f3543029.deta.app/docs


