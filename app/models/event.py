from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.session import Base
import uuid

class Event(Base):
    __tablename__ = "events"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # остальные поля добавим позже
