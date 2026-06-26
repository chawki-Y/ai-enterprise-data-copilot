# Trade Operations Copilot

An embeddable AI copilot for trade operations and middle-office dashboards.

The project provides a reusable browser widget that opens as a right-side assistant panel from a floating button. It can be imported into any website with one script tag, while the standalone template page lets the copilot be tested on its own.

The current agent is tailored for a trade operations dashboard that exposes trade, operations, market data, audit, and investigation APIs.

## What It Does

- Embeds into any HTML, React, or server-rendered website
- Shows a floating `Ask Copilot` button on the right side of the screen
- Opens a right-side popup panel with a chat-style assistant
- Calls a FastAPI copilot backend
- Uses the existing Trade Operations API as its tool source
- Answers analyst questions about trades, rejected trades, market data, audit logs, P&L, and operational risk
- Keeps a standalone demo UI for testing without importing into another project

## Architecture

```mermaid
flowchart LR
    Website[Host website] --> Widget[Embeddable JS widget]
    Template[Standalone template UI] --> Widget
    Widget --> CopilotAPI[FastAPI copilot backend]
    CopilotAPI --> Agent[Trade operations agent service]
    Agent --> TradeAPI[Existing Node/Express Trade Operations API]
    TradeAPI --> DB[(PostgreSQL)]
    Agent --> OpenAI[Optional OpenAI summarization]
    CopilotAPI --> Widget
```

## Repository Structure

```text
backend/
  app/api/routes.py                 FastAPI routes
  app/services/trade_ops_agent.py   Agent intent routing and answers
  app/services/trade_ops_client.py  Client for the host Trade Operations API
  app/schemas/agent.py              Agent request/response contracts

frontend/
  public/trade-ops-copilot.js       Importable widget bundle
  src/App.jsx                       Standalone template UI

database/
  schema.sql, seed.sql              Legacy standalone demo database assets
```

## Import Into Any Website

Serve or copy `frontend/public/trade-ops-copilot.js`, then add:

```html
<script src="/trade-ops-copilot.js"></script>
<script>
  window.TradeOpsCopilot.init({
    apiBaseUrl: "http://127.0.0.1:8000",
    title: "Trade Ops Copilot",
    subtitle: "Middle-office assistant",
    buttonLabel: "Ask Copilot"
  });
</script>
```

The widget creates its own floating button, panel, styles, chat messages, sample questions, and result previews.

## Backend Endpoints

Primary widget endpoints:

- `GET /agent/sample-questions`
- `POST /agent/ask`

Utility endpoints:

- `GET /health`
- `GET /schema`
- `GET /sample-questions`
- `POST /ask`
- `GET /query-history`

## Supported Questions

Examples:

- Give me an operations morning summary.
- Show me today's rejected trades.
- Why was trade TRD-20260625-000004 rejected?
- Summarize audit logs for trade TRD-20260625-000004.
- Is any market data stale?
- What happened with AAPL market price?
- Summarize today's P&L.
- Highlight operational risks.

## Environment Variables

Backend:

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/enterprise_copilot
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3001,http://127.0.0.1:5173,http://127.0.0.1:3001
TRADE_OPS_API_BASE_URL=http://localhost:3001
```

Frontend:

```text
VITE_API_BASE_URL=
```

## Run Standalone

Start the Trade Operations app first, because the copilot agent reads from its API.

Then run the copilot backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Run the standalone template:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Run Embedded In The Trade Operations App

The host app can load `trade-ops-copilot.js` from its own `public/` folder or from the copilot dev server.

For local development:

1. Start the Trade Operations app on port `3001`.
2. Start this FastAPI copilot backend on port `8000`.
3. Open the Trade Operations website.
4. Click the floating `Ask Copilot` button.

## Agent Design

The agent uses the existing system API instead of duplicating business rules:

- `/api/operations/summary`
- `/api/operations/investigate/:tradeId`
- `/api/trades`
- `/api/trades/report`
- `/api/market-overview`
- `/api/market-price/:symbol`
- `/api/audit-logs`

This keeps the copilot aligned with the source system and makes the widget portable.

## Tests

```bash
cd backend
pytest
```

## Future Improvements

- Conversation memory
- Streaming responses
- User/session context from the host app
- Deeper tool calling with structured action plans
- Theming options for host applications
- Authentication between the host website and copilot backend
