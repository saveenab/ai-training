# Saveena Boga - Models

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Classification(Base):
    __tablename__ = "classifications"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    label = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)