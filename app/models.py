from sqlalchemy import Column, Integer, Text, TIMESTAMP, CheckConstraint, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    issue = Column(Text, nullable=False)
    priority = Column(Text, nullable=False)
    status = Column(Text, default="pending")
    is_deleted = Column(Boolean, default=False)
    is_saved = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "priority IN ('High', 'Medium', 'Low')",
            name="check_priority_valid"
        ),
        CheckConstraint(
            "status IN ('pending', 'inprogress', 'completed', 'cancelled')",
            name="check_status_valid"
        ),
    )