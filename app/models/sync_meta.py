from sqlalchemy import Column, String, DateTime, Integer
from app.db.session import Base

class SyncMeta(Base):
    __tablename__ = "sync_meta"
    id = Column(Integer, primary_key=True, index=True)
    last_sync_time = Column(DateTime(timezone=True), nullable=True)
    last_changed_at = Column(String, nullable=True)  # дата для changed_at
    status = Column(String, default="idle")