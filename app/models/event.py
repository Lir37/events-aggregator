import uuid
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.session import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    place_id = Column(PGUUID(as_uuid=True), nullable=True)
    place_name = Column(String, nullable=True)
    place_city = Column(String, nullable=True)
    place_address = Column(String, nullable=True)
    seats_pattern = Column(String, nullable=True)
    event_time = Column(DateTime(timezone=True), nullable=True)
    registration_deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=True)
    number_of_visitors = Column(Integer, default=0)
    changed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    status_changed_at = Column(DateTime(timezone=True), nullable=True)
