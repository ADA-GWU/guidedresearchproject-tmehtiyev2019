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

Refer to the API documentation for detailed information on request/response payloads and usage.


## Access the microservice at
http://localhost:8001

## How to Run

1. Install Docker on your machine.

2. Build the Docker image:
   ```bash
   docker build -t product-catalog-microservice 

3. Run the Docker container:
  ```bash
   docker run -d -p 8001:8001 product-catalog-microservice 



