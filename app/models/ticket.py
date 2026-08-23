from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
import uuid

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    ticket_id = Column(String, unique=True, nullable=False)  # внешний ticket_id
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    seat = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="now()")
