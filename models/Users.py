from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy import String, Column, DateTime, Integer

from tools.Database import Base


class UsersModel(Base):

    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)
    is_authenticated = Column(Integer, server_default=str(0))
    active = Column(Integer, server_default=str(1))
    created_at = Column(DateTime, default=current_timestamp())
    updated_at = Column(
        DateTime, default=current_timestamp(), onupdate=current_timestamp()
    )

    def __init__(self, **kwargs):

        self.user_id = kwargs['user_id']
        self.username = kwargs['username']
        self.email = kwargs['email']
        self.password = kwargs['password']
        self.is_authenticated = kwargs['is_authenticated']
        self.active = kwargs['active']
        self.created_at = kwargs['created_at']
        self.updated_at = kwargs['updated_at']
