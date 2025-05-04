from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy import String, Column, Integer, Numeric, DateTime

from tools.Database import Base


class ProductModel(Base):

    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    in_stock = Column(Integer, server_default=str(1))
    quantity = Column(Integer, nullable=False)
    category = Column(String(255))
    active = Column(Integer, server_default=str(1))
    created_at = Column(DateTime, default=current_timestamp())
    updated_at = Column(
        DateTime, default=current_timestamp(), onupdate=current_timestamp()
    )

    def __init__(self, **kwargs):

        self.product_id = kwargs['product_id']
        self.name = kwargs['name']
        self.price = kwargs['price']
        self.in_stock = kwargs['in_stock']
        self.quantity = kwargs['quantity']
        self.category = kwargs['category']
        self.active = kwargs['active']
        self.created_at = kwargs['created_at']
        self.updated_at = kwargs['updated_at']
