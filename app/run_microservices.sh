#!/bin/bash

# Run the Product Catalog Microservice
cd product_service
uvicorn product_service:app --host 0.0.0.0 --port 8001 &

# Run the Shopping Cart Microservice
cd ../cart_service
uvicorn cart_service:app --host 0.0.0.0 --port 8002 &

# Run the Order Management Microservice
cd ../order_service
uvicorn order_service:app --host 0.0.0.0 --port 8003 &

# Wait for the microservices to start
sleep 5

# Add delay to ensure all services are up before running tests or other operations

# Run tests or perform other operations, if needed

# Kill the microservices processes
kill $(jobs -p)
