# IncidentLoop — Production Incident Memory System (v2)

**IncidentLoop** is a production incident memory system that captures root cause solutions and verified outcomes from past failures, surfacing relevant historical fixes when similar incidents occur. It includes a **Silent Failure Detector** (catching traffic drop anomalies with zero error logs) and a **Technical Debt Radar** (flagging repeatedly failing endpoints).

---

## Key Features

1. **Incident Memory Engine**: Calculates vector text & field similarity matching target incidents against past resolved incidents with detailed evidence breakdowns.
2. **Human-in-the-Loop Approval**: No fix is ever auto-applied. Engineers review similarity matches and choose between **"Use Previous Fix"** or **"Investigate New"**.
3. **Silent Failure Detector**: Evaluates activity baselines to catch silent service outages even when zero exception logs are recorded.
4. **Technical Debt Radar**: Tracks recurrence signatures (`service:endpoint:error_type`) and alerts when endpoints exceed failure thresholds.

---

## Project Structure

```
ilproject/
├── backend/
│   ├── app/
│   │   ├── constants.py      # Centralized API route definitions
│   │   ├── database.py       # SQLite database configuration
│   │   ├── main.py           # FastAPI application entrypoint
│   │   ├── matcher.py        # TF-IDF & weighted similarity matcher
│   │   ├── models.py         # SQLAlchemy schemas (incidents, baselines, recurrence_groups)
│   │   ├── seed_data.py      # 8 historical incidents & demo seeder
│   │   └── routers/          # API route handlers
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── config.js     # Single source of truth for frontend API URLs
│   │   │   └── client.js     # Fetch API client wrapper
│   │   ├── components/       # Header, DemoBar, IncidentList, MatchModal, SilentPanel, DebtRadar
│   │   ├── App.jsx           # Main React Dashboard
│   │   └── App.css           # Glassmorphism dark theme styling
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Prerequisites

- **Python**: 3.10+
- **Node.js**: 18+ & `npm`

---

## Quick Start (Run Locally)

### 1. Start FastAPI Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
```
*Backend API server will run at `http://127.0.0.1:8000`. Swagger API docs available at `http://127.0.0.1:8000/docs`.*

### 2. Start React Frontend Dashboard

In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*Frontend dev server will run at `http://127.0.0.1:3000`.*

---

## Interactive Demo Controls

Open `http://127.0.0.1:3000` in your browser to interact with the dashboard:

1. **Reset & Seed**: Resets SQLite database and populates 8 historical incidents (including duplicate target and `/login` technical debt).
2. **Trigger Duplicate Incident**: Spawns a new OPEN incident on `/login` that immediately triggers a **94.5% similarity match** against historical Database Pool Exhaustion.
3. **Simulate Silent Drop**: Ages traffic baseline on `payment-service:/checkout` to trigger a silent drop anomaly without error logs.
4. **Use Previous Fix**: Copies verified root cause and fix details from the top historical match to resolve the incident.
5. **Investigate New**: Allows submitting a novel root cause, fix description, and PR link for custom incident resolution.
