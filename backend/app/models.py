import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    service = Column(String(100), index=True, nullable=False)
    endpoint = Column(String(255), index=True, nullable=False)
    error_type = Column(String(150), index=True, nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    category = Column(String(100), default="General", index=True)
    embedding = Column(Text, nullable=True)  # JSON or TF-IDF feature representations
    root_cause = Column(Text, nullable=True)
    fix_description = Column(Text, nullable=True)
    fix_pr_url = Column(String(255), nullable=True)
    status = Column(String(50), default="OPEN", index=True)  # OPEN, RESOLVED, INVESTIGATING
    resolution_verified = Column(Boolean, default=False)

class ActivityBaseline(Base):
    __tablename__ = "activity_baselines"

    id = Column(Integer, primary_key=True, index=True)
    service_endpoint = Column(String(255), unique=True, index=True, nullable=False) # e.g. "auth-service:/login"
    expected_rate = Column(Float, default=100.0) # Requests per window
    window = Column(Integer, default=300) # In seconds
    last_seen_at = Column(DateTime, default=datetime.datetime.utcnow)
    anomaly_threshold = Column(Float, default=0.8) # 80% drop threshold

class RecurrenceGroup(Base):
    __tablename__ = "recurrence_groups"

    id = Column(Integer, primary_key=True, index=True)
    signature = Column(String(255), unique=True, index=True, nullable=False) # e.g. "auth-service:/login:DatabaseTimeoutError"
    occurrence_count = Column(Integer, default=1)
    first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    flagged_as_debt = Column(Boolean, default=False)
    recommendation = Column(Text, nullable=True)
