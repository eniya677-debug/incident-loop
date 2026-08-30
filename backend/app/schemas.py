import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

# --- Incident Schemas ---

class IncidentCreate(BaseModel):
    service: str
    endpoint: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = ""
    category: Optional[str] = "General"

class IncidentResolve(BaseModel):
    root_cause: str
    fix_description: str
    fix_pr_url: Optional[str] = ""
    resolution_verified: Optional[bool] = True

class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime.datetime
    service: str
    endpoint: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    category: str
    embedding: Optional[str] = None
    root_cause: Optional[str] = None
    fix_description: Optional[str] = None
    fix_pr_url: Optional[str] = None
    status: str
    resolution_verified: bool

class MatchEvidence(BaseModel):
    endpoint_score: float
    error_type_score: float
    message_tfidf_score: float
    stack_tfidf_score: float

class MatchResult(BaseModel):
    incident: IncidentOut
    similarity_score: float # 0.0 to 100.0
    evidence: MatchEvidence

class MatchListResponse(BaseModel):
    target_incident_id: int
    matches: List[MatchResult]

# --- Baseline & Silent Failure Schemas ---

class HeartbeatCreate(BaseModel):
    service: str
    endpoint: str

class ActivityBaselineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_endpoint: str
    expected_rate: float
    window: int
    last_seen_at: datetime.datetime
    anomaly_threshold: float

class SilentFailureOut(BaseModel):
    service: str
    endpoint: str
    service_endpoint: str
    seconds_inactive: float
    window: int
    last_seen_at: datetime.datetime
    status: str
    severity: str
    recommendation: str

# --- Technical Debt Schemas ---

class TechnicalDebtOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    signature: str
    service: str
    endpoint: str
    error_type: str
    occurrence_count: int
    first_seen: datetime.datetime
    last_seen: datetime.datetime
    flagged_as_debt: bool
    recommendation: Optional[str] = None

# --- Action Responses ---
class GenericResponse(BaseModel):
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None
