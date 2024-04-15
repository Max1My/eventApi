from sqlalchemy import Column, Integer


class PrimaryKeyMixin:
    id = Column(Integer, autoincrement=True, primary_key=True)
