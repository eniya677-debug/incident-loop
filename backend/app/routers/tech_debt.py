from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RecurrenceGroup
from app.schemas import TechnicalDebtOut
from app.constants import ROUTE_TECHNICAL_DEBT

router = APIRouter(tags=["Technical Debt Detection"])

@router.get(ROUTE_TECHNICAL_DEBT, response_model=List[TechnicalDebtOut])
def get_technical_debt(db: Session = Depends(get_db)):
    """
    Core Feature: Technical Debt Detector.
    Returns failure signature groups flagged as technical debt or exceeding recurrence threshold.
    """
    groups = db.query(RecurrenceGroup).order_by(RecurrenceGroup.occurrence_count.desc()).all()
    results = []

    for g in groups:
        parts = g.signature.split(":")
        service = parts[0] if len(parts) > 0 else "unknown"
        endpoint = parts[1] if len(parts) > 1 else "unknown"
        error_type = parts[2] if len(parts) > 2 else "MULTIPLE_ERRORS"

        results.append(TechnicalDebtOut(
            id=g.id,
            signature=g.signature,
            service=service,
            endpoint=endpoint,
            error_type=error_type,
            occurrence_count=g.occurrence_count,
            first_seen=g.first_seen,
            last_seen=g.last_seen,
            flagged_as_debt=g.flagged_as_debt or (g.occurrence_count >= 3),
            recommendation=g.recommendation or f"Repeated failures ({g.occurrence_count}) detected on {endpoint}."
        ))

    return results
