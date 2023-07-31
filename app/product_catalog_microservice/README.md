# Product Catalog Microservice

This microservice is responsible for managing the product inventory, details, and availability.


## API Documentation
#### GET /products:

Get all products.

#### Response
`200 OK`: Successful operation. Returns a list of products.


```
@app.get("/products")
def get_products():
    cur.execute("""SELECT * FROM products""")
    products=cur.fetchall()
    # print(products)
    return {"data":products}
```

#### GET /products/{product_id}:

Returns the product with the specified ID.

#### Parameters
`product_id`: ID of the product to retrieve.

#### Response
`200 OK`: Successful operation. Returns the product with the specified ID.

`404 Not Found`: Product with the specified ID not found.


```
@app.get("/products/{product_id}")
def get_product(product_id: int):
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with id: {product_id} was not found")
    return {"product_detail":product}
```

#### POST /products:
Creates a new product in the catalog.

#### Request Body
`name (string)`: Name of the product.

`price (integer)`: Price of the product.

`quantity (integer)`: Quantity of the product in the inventory.

#### Response

`201 Created`: Product created successfully.

`500 Internal Server Error`: Failed to create the product.


```
@app.post("/products", status_code=status.HTTP_201_CREATED )
def add_product(product: Product):
    cur.execute(
        """INSERT INTO products ( name, price, quantity) VALUES (%s, %s, %s) RETURNING * """,
        ( product.name, product.price, product.quantity)
    )
    new_product=cur.fetchone()
    conn.commit()
    return {"data": new_product}
```

#### PUT /products/{product_id}:
Updates the specified product in the catalog.

#### Parameters
`product_id`: ID of the product to update.

#### Request Body
`name (string)`: New name of the product.

`price (integer)`: New price of the product.

`quantity (integer)`: New quantity of the product in the inventory.

#### Response
`200 OK`: Successful operation. Product updated successfully.

`404 Not Found`: Product with the specified ID not found.


```
@app.put("/products/{product_id}")
def update_product(product_id: int, updated_product: Product):
    # check if product exists
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with id: {product_id} was not found")
    
    # update the product
    cur.execute(
        """UPDATE products 
           SET name = %s, price = %s, quantity = %s 
           WHERE id = %s RETURNING *""",
        (updated_product.name, updated_product.price, updated_product.quantity, product_id)
    )
    conn.commit()
    updated_product = cur.fetchone()

    return {"message": "Product updated successfully", "updated_product": updated_product}

```

#### DELETE /products/{product_id}:
Deletes the specified product from the catalog.

#### Parameters
product_id: ID of the product to delete.

#### Response
`204 No Content`: Product deleted successfully.

`404 Not Found`: Product with the specified ID not found.


```
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"product with id: {product_id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

## Dependencies

This service is independent and does not have any dependencies.

## Database Connection

This service uses PostgreSQL as its database which is deployed on Amazon RDS. It connects to the PostgreSQL instance using the psycopg2 library. The database connection parameters are specified within the application code, including the database name, user, password, host, and port.

Upon application start-up, the service automatically connects to the database using the provided credentials and host information. The code then checks for the existence of necessary tables (products) and creates them if they do not exist.


```
try:
    conn = psycopg2.connect(
        dbname='product_catalog_db',
        user='postgres',
        password="qwer1234!",
        host='database-1.cyxnkg8bocgc.us-east-2.rds.amazonaws.com',
        port="5432",
        cursor_factory=RealDictCursor
    )
except psycopg2.Error as e:
    print("Unable to connect to the database")
```


### Database Tables
There is one table created within this service:

#### products: This table stores the details of all products in the catalog. It has four fields:
`id` : A unique identifier for the product.

`name`: The name of the product.

`price`: The price of the product.

`quantity`: The quantity of the product in the inventory.


```
try:
    cur = conn.cursor()

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS products(
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        price INTEGER NOT NULL,
        quantity INTEGER NOT NULL
    )
    '''

    cur.execute(create_table_query)
    conn.commit()
    print("Table created successfully")

except psycopg2.Error as e:
    print("An error occurred while creating the table:", e)

```

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
https://product_catalog-1-w1405204.deta.app/

Refer to the API documentation for detailed information on request/response payloads and usage.

## Access the API documentation at Swagger UI
https://product_catalog-1-w1405204.deta.app/docs


## Access the Postman API Test Collection:
app/Postman API Test Collection