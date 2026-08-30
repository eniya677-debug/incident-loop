import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Incident, RecurrenceGroup
from app.schemas import (
    IncidentCreate, IncidentResolve, IncidentOut,
    MatchListResponse, GenericResponse
)
from app.matcher import find_similar_incidents
from app.constants import ROUTE_INCIDENTS, ROUTE_INCIDENT_DETAIL, ROUTE_INCIDENT_MATCHES, ROUTE_INCIDENT_RESOLVE, TECH_DEBT_RECURRENCE_THRESHOLD

router = APIRouter(tags=["Incidents"])

@router.post(ROUTE_INCIDENTS, response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    """
    Log a new incident (error_type, error_message, endpoint, service, stack_trace).
    Automatically updates recurrence groups & flags technical debt if recurrence >= threshold.
    """
    new_inc = Incident(
        service=payload.service,
        endpoint=payload.endpoint,
        error_type=payload.error_type,
        error_message=payload.error_message,
        stack_trace=payload.stack_trace,
        category=payload.category or "General",
        status="OPEN",
        resolution_verified=False
    )
    db.add(new_inc)
    db.commit()
    db.refresh(new_inc)

    # Update Recurrence Group for Technical Debt Detector
    sig = f"{payload.service}:{payload.endpoint}:{payload.error_type}"
    rec = db.query(RecurrenceGroup).filter(RecurrenceGroup.signature == sig).first()
    now = datetime.datetime.utcnow()

    if rec:
        rec.occurrence_count += 1
        rec.last_seen = now
        if rec.occurrence_count >= TECH_DEBT_RECURRENCE_THRESHOLD:
            rec.flagged_as_debt = True
            rec.recommendation = (
                f"RECURRING FAILURE ALERT: Endpoint {payload.endpoint} on service {payload.service} "
                f"has failed {rec.occurrence_count} times with {payload.error_type}. Refactoring recommended."
            )
    else:
        rec = RecurrenceGroup(
            signature=sig,
            occurrence_count=1,
            first_seen=now,
            last_seen=now,
            flagged_as_debt=False,
            recommendation=f"Initial failure signature recorded for {payload.endpoint}."
        )
        db.add(rec)
    db.commit()

    return new_inc

@router.get(ROUTE_INCIDENTS, response_model=List[IncidentOut])
def list_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    service_filter: Optional[str] = Query(None, alias="service"),
    db: Session = Depends(get_db)
):
    """List all incidents ordered by creation date descending."""
    query = db.query(Incident)
    if status_filter:
        query = query.filter(Incident.status == status_filter.upper())
    if service_filter:
        query = query.filter(Incident.service == service_filter)
    return query.order_by(Incident.created_at.desc()).all()

@router.get(ROUTE_INCIDENT_DETAIL, response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Fetch details of a single incident."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return inc

@router.get(ROUTE_INCIDENT_MATCHES, response_model=MatchListResponse)
def get_incident_matches(incident_id: int, db: Session = Depends(get_db)):
    """
    Core Feature: Similarity matching engine.
    Finds historical resolved incidents matching the given target incident.
    Returns ranked similarity percentage and detailed evidence breakdown.
    """
    target = db.query(Incident).filter(Incident.id == incident_id).first()
    if not target:
        raise HTTPException(status_code=404, detail=f"Target incident {incident_id} not found")

    # Retrieve all resolved historical incidents
    historical = db.query(Incident).filter(
        Incident.id != incident_id,
        Incident.status == "RESOLVED"
    ).all()

    matches = find_similar_incidents(target, historical)

    return {
        "target_incident_id": incident_id,
        "matches": matches
    }

@router.post(ROUTE_INCIDENT_RESOLVE, response_model=GenericResponse)
def resolve_incident(
    incident_id: int,
    payload: IncidentResolve,
    db: Session = Depends(get_db)
):
    """
    Human-in-the-Loop Resolution:
    Logs root_cause, fix_description, and fix_pr_url to strengthen system memory.
    Strictly requires human trigger (Use Previous Fix or Investigate New).
    """
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    inc.root_cause = payload.root_cause
    inc.fix_description = payload.fix_description
    inc.fix_pr_url = payload.fix_pr_url or ""
    inc.status = "RESOLVED"
    inc.resolution_verified = payload.resolution_verified if payload.resolution_verified is not None else True
    db.commit()
    db.refresh(inc)

    return GenericResponse(
        status="success",
        message=f"Incident #{incident_id} resolved and memory updated.",
        details={
            "incident_id": inc.id,
            "root_cause": inc.root_cause,
            "fix_description": inc.fix_description,
            "status": inc.status
        }
    )
