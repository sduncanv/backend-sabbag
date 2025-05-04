from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy import String, Column, DateTime, Integer

from tools.Database import Base


class RolesModel(Base):

    __tablename__ = 'roles'

    rol_id = Column(Integer, primary_key=True)
    rol_name = Column(String(255), nullable=False)
    active = Column(Integer, server_default=str(1))
    created_at = Column(DateTime, default=current_timestamp())
    updated_at = Column(
        DateTime, default=current_timestamp(), onupdate=current_timestamp()
    )

    def __init__(self, **kwargs):

        self.rol_id = kwargs['rol_id']
        self.rol_name = kwargs['rol_name']
        self.active = kwargs['active']
        self.created_at = kwargs['created_at']
        self.updated_at = kwargs['updated_at']
