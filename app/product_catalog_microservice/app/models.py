import database
from sqlalchemy import Column, Integer, String, Boolean

class Product(Base):
    __tablename__="products_test"
    id=Column(Integer, primary_key=True, nullable=False)
    name=Column(String,nullable=False )
    price=Column(Integer,nullable=False)
    quantity=Column(Integer,nullable=False)