"""
Centralized API route definitions and constants for IncidentLoop Backend.
"""

API_PREFIX = "/api"

# Incident Routes
ROUTE_INCIDENTS = "/incidents"
ROUTE_INCIDENT_DETAIL = "/incidents/{incident_id}"
ROUTE_INCIDENT_MATCHES = "/incidents/{incident_id}/matches"
ROUTE_INCIDENT_RESOLVE = "/incidents/{incident_id}/resolve"

# Activity & Silent Failure Routes
ROUTE_HEARTBEAT = "/activity-heartbeat"
ROUTE_SILENT_FAILURES = "/silent-failures"
ROUTE_BASELINES = "/activity-baselines"

# Technical Debt Routes
ROUTE_TECHNICAL_DEBT = "/technical-debt"

# Demo Routes
ROUTE_SEED = "/seed"
ROUTE_TRIGGER_DUPLICATE = "/trigger-duplicate"
ROUTE_SIMULATE_SILENT_DROP = "/simulate-silent-drop"

# Recurrence Threshold for Technical Debt
TECH_DEBT_RECURRENCE_THRESHOLD = 3
