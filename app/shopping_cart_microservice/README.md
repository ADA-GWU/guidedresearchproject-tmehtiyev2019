# Shopping Cart Microservice

This microservice handles the management of customer shopping carts.

## API Documentation

GET /carts:
Get all carts.

POST /carts: 
Create a new cart.

PUT /carts/{cart_id}: 
Update cart by ID.

DELETE /carts/{cart_id}: 
Delete cart by ID.

Refer to the API documentation for detailed information on request/response payloads and usage.




## Access the microservice at
http://localhost:8002


## How to Run

1. Install Docker on your machine.

2. Build the Docker image:
   ```bash
   docker build -t shopping-cart-microservice .

3. Run the Docker container:
  ```bash
   docker run -d -p 8002:8002 shopping-cart-microservice