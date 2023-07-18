
**Shopping Cart Microservice:**

Dockerfile:
```Dockerfile
# Use a base image with Python runtime
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY app /app

# Expose the port number on which the microservice will listen
EXPOSE 8002

# Run the microservice
CMD ["uvicorn", "cart_service:app", "--host", "0.0.0.0", "--port", "8002"]
