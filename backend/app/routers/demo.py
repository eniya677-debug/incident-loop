import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.seed_data import seed_database
from app.models import Incident, ActivityBaseline, RecurrenceGroup
from app.schemas import GenericResponse, IncidentOut
from app.constants import ROUTE_SEED, ROUTE_TRIGGER_DUPLICATE, ROUTE_SIMULATE_SILENT_DROP, TECH_DEBT_RECURRENCE_THRESHOLD

router = APIRouter(tags=["Demo Triggers"])

@router.post(ROUTE_SEED, response_model=GenericResponse)
def seed_demo_data(db: Session = Depends(get_db)):
    """
    Demo Button 1: Reset & Seed
    Resets database and populates 8 historical incidents, 3 baselines, and technical debt groups.
    """
    res = seed_database(db)
    return GenericResponse(
        status="success",
        message="Database successfully reset and seeded with 8 historical incidents!",
        details=res
    )

@router.post(ROUTE_TRIGGER_DUPLICATE, response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def trigger_duplicate_incident(db: Session = Depends(get_db)):
    """
    Demo Button 2: Trigger Duplicate Incident
    Creates a brand new OPEN incident matching the historical Database Connection Pool Exhaustion on /login.
    This demonstrates immediate high similarity match (>90%) with past fix & root cause!
    """
    now = datetime.datetime.utcnow()
    new_inc = Incident(
        created_at=now,
        service="auth-service",
        endpoint="/login",
        error_type="DatabaseTimeoutError",
        error_message="Connection to Postgres pool timed out after 3000ms waiting for available client during peak load",
        stack_trace="Traceback (most recent call last):\n  File \"/app/auth/db.py\", line 42, in get_user\n    conn = pool.get_connection(timeout=3.0)\n  File \"/app/db/pool.py\", line 110, in get_connection\n    raise DatabaseTimeoutError(\"Pool exhausted\")",
        category="Database",
        status="OPEN",
        resolution_verified=False
    )
    db.add(new_inc)
    db.commit()
    db.refresh(new_inc)

    # Update Recurrence Group for Technical Debt
    sig = "auth-service:/login:DatabaseTimeoutError"
    rec = db.query(RecurrenceGroup).filter(RecurrenceGroup.signature == sig).first()
    if rec:
        rec.occurrence_count += 1
        rec.last_seen = now
        if rec.occurrence_count >= TECH_DEBT_RECURRENCE_THRESHOLD:
            rec.flagged_as_debt = True
            rec.recommendation = f"CRITICAL RECURRENCE: {rec.occurrence_count} DB timeouts on /login!"
    else:
        rec = RecurrenceGroup(
            signature=sig,
            occurrence_count=1,
            first_seen=now,
            last_seen=now,
            flagged_as_debt=False
        )
        db.add(rec)
    db.commit()

    return new_inc

@router.post(ROUTE_SIMULATE_SILENT_DROP, response_model=GenericResponse)
def simulate_silent_drop(db: Session = Depends(get_db)):
    """
    Demo Button 3: Simulate Silent Drop
    Manually ages the last_seen_at timestamp of payment-service:/checkout baseline to 15 minutes ago.
    This triggers silent failure drop detection without generating any error logs!
    """
    svc_end = "payment-service:/checkout"
    base = db.query(ActivityBaseline).filter(ActivityBaseline.service_endpoint == svc_end).first()
    now = datetime.datetime.utcnow()
    past_time = now - datetime.timedelta(minutes=15)

    if not base:
        base = ActivityBaseline(
            service_endpoint=svc_end,
            expected_rate=120.0,
            window=300,
            last_seen_at=past_time,
            anomaly_threshold=0.8
        )
        db.add(base)
    else:
        base.last_seen_at = past_time

    db.commit()

    return GenericResponse(
        status="success",
        message=f"Simulated silent drop on {svc_end}! Last seen set to 15 minutes ago.",
        details={
            "service_endpoint": svc_end,
            "last_seen_at": past_time.isoformat(),
            "window_seconds": 300
        }
    )
