import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ActivityBaseline
from app.schemas import (
    HeartbeatCreate, ActivityBaselineOut, SilentFailureOut, GenericResponse
)
from app.constants import ROUTE_HEARTBEAT, ROUTE_SILENT_FAILURES, ROUTE_BASELINES

router = APIRouter(tags=["Silent Failure Detection"])

@router.post(ROUTE_HEARTBEAT, response_model=GenericResponse)
def record_heartbeat(payload: HeartbeatCreate, db: Session = Depends(get_db)):
    """
    Record normal system traffic/heartbeat for a service endpoint.
    Updates `last_seen_at` baseline timestamp.
    """
    svc_end = f"{payload.service}:{payload.endpoint}"
    base = db.query(ActivityBaseline).filter(ActivityBaseline.service_endpoint == svc_end).first()
    now = datetime.datetime.utcnow()

    if base:
        base.last_seen_at = now
    else:
        base = ActivityBaseline(
            service_endpoint=svc_end,
            expected_rate=100.0,
            window=300,
            last_seen_at=now,
            anomaly_threshold=0.8
        )
        db.add(base)
    db.commit()

    return GenericResponse(
        status="success",
        message=f"Heartbeat recorded for {svc_end}",
        details={"service_endpoint": svc_end, "last_seen_at": now.isoformat()}
    )

@router.get(ROUTE_BASELINES, response_model=List[ActivityBaselineOut])
def get_baselines(db: Session = Depends(get_db)):
    """List all registered service endpoint activity baselines."""
    return db.query(ActivityBaseline).all()

@router.get(ROUTE_SILENT_FAILURES, response_model=List[SilentFailureOut])
def detect_silent_failures(db: Session = Depends(get_db)):
    """
    Core Feature: Silent Failure Detector.
    Scans `activity_baselines` for endpoints where traffic has stopped or dropped below anomaly thresholds,
    EVEN IF ZERO ERROR LOGS HAVE BEEN FIRED.
    """
    baselines = db.query(ActivityBaseline).all()
    now = datetime.datetime.utcnow()
    silent_drops = []

    for b in baselines:
        elapsed_seconds = (now - b.last_seen_at).total_seconds()
        # If elapsed time exceeds the expected window (e.g. 300s / 5min)
        if elapsed_seconds > b.window:
            parts = b.service_endpoint.split(":", 1)
            service = parts[0] if len(parts) > 0 else "unknown"
            endpoint = parts[1] if len(parts) > 1 else b.service_endpoint

            silent_drops.append({
                "service": service,
                "endpoint": endpoint,
                "service_endpoint": b.service_endpoint,
                "seconds_inactive": round(elapsed_seconds, 1),
                "window": b.window,
                "last_seen_at": b.last_seen_at,
                "status": "SILENT_DROP_DETECTED",
                "severity": "CRITICAL" if elapsed_seconds > (b.window * 2) else "WARNING",
                "recommendation": f"Traffic on {b.service_endpoint} stopped {round(elapsed_seconds/60, 1)} minutes ago with 0 logged exceptions! Check upstream load balancer or network gateway."
            })

    return silent_drops
