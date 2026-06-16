# OOH Agentic System

A small agent-powered digital out-of-home advertising demo. The backend uses live weather, local event data, and Claude to choose the best creative for a selected billboard. The frontend displays the decision, confidence score, creative rankings, reasoning, and agent trace.

## Project Structure

```text
backend/
  main.py          FastAPI app and API routes
  agent.py         Claude decision agent and tool-calling flow
  weather.py       OpenWeather integration
  events.py        Ticketmaster integration
  data.py          Billboard and creative inventory

frontend/
  src/             React app and UI components
  vite.config.js   Vite config with /api proxy to FastAPI
```

## Requirements

- Python 3.13+
- Node.js 18+
- npm
- API keys for:
  - Anthropic
  - OpenWeather
  - Ticketmaster

## Environment

Create `backend/.env`:

```bash
ANTHROPIC_API_KEY=your_anthropic_key
OPENWEATHER_API_KEY=your_openweather_key
TICKETMASTER_API_KEY=your_ticketmaster_key
```

Optional:

```bash
ANTHROPIC_MODEL=claude-sonnet-4-6
```

## Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Backend URL:

```text
http://127.0.0.1:8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Frontend URL:

```text
http://127.0.0.1:5173
```

If port `5173` is busy, Vite will choose the next available port.

## API Endpoints

```text
GET /billboards
GET /creatives
GET /decision/{billboard_id}
```

Example decision route:

```text
http://127.0.0.1:8000/decision/billboard_1
```

## Frontend Features

- Billboard selector for Miami, NYC, and Chicago
- Current weather panel
- Local events panel
- Selected creative panel
- Confidence score
- Creative scoring/ranking bars
- Reasoning summary
- Agent trace showing weather, events, evaluation, and final decision

## Build

```bash
cd frontend
npm run build
```

The production build is written to `frontend/dist/`.
