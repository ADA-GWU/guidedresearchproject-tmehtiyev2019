from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"data": "test post"}

@app.get("/")
async def root():
    return {"message": "Hi edited"}

# @app.get("/posts/")
# async def root():
#     return {"data": "test post"}

