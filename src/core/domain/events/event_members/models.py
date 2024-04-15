from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.mixins.models import PrimaryKeyMixin
from src.core.domain.events.models import Event
from src.core.domain.users.models import User
from src.db.engine import Base


class EventMembers(Base, PrimaryKeyMixin):
    __tablename__ = 'event_members'
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events.id'))
    event = relationship(
        Event,
        lazy='joined',
        viewonly=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user = relationship(
        User,
        lazy='joined',
        viewonly=True
    )
