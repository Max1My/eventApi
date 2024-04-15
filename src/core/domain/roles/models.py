from sqlalchemy import String, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.engine import Base


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    user = relationship('User', back_populates='role', cascade='save-update, merge, delete')
