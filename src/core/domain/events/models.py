from sqlalchemy import Column, String, DateTime

from src.common.mixins.models import PrimaryKeyMixin
from src.db.engine import Base


class Event(Base, PrimaryKeyMixin):
    __tablename__ = 'events'
    name = Column(String)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
