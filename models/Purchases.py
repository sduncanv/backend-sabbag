from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy import Column, DateTime, Integer

from tools.Database import Base


class PurchasesModel(Base):

    __tablename__ = 'purchases'

    purchase_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    active = Column(Integer, server_default=str(1))
    created_at = Column(DateTime, default=current_timestamp())
    updated_at = Column(
        DateTime, default=current_timestamp(), onupdate=current_timestamp()
    )

    def __init__(self, **kwargs):

        self.purchase_id = kwargs['purchase_id']
        self.user_id = kwargs['user_id']
        self.product_id = kwargs['product_id']
        self.active = kwargs['active']
        self.created_at = kwargs['created_at']
        self.updated_at = kwargs['updated_at']
