from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy import String, Column, DateTime, Integer

from tools.Database import Base


class UsersRolesModel(Base):

    __tablename__ = 'users_roles'

    user_role_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    role_id = Column(Integer, nullable=False)
    active = Column(Integer, server_default=str(1))
    created_at = Column(DateTime, default=current_timestamp())
    updated_at = Column(
        DateTime, default=current_timestamp(), onupdate=current_timestamp()
    )

    def __init__(self, **kwargs):

        self.user_role_id = kwargs['user_role_id']
        self.user_id = kwargs['user_id']
        self.role_id = kwargs['role_id']
        self.active = kwargs['active']
        self.created_at = kwargs['created_at']
        self.updated_at = kwargs['updated_at']
