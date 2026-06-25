# Capital Markets Data Copilot

A full-stack portfolio project that combines capital-markets domain modeling, safe SQL generation, API design, and a polished React interface.

The app lets a user ask trade-lifecycle questions in natural language. The backend generates a PostgreSQL `SELECT` query, validates it through strict guardrails, executes it against a capital-markets dataset, stores query history, and returns a natural-language answer, generated SQL, and result table.

## Domain Context

Trading and post-trade platforms sit at the intersection of front office, operations, risk, market data, and settlement workflows. This project models those workflows through trades, books, portfolios, counterparties, instruments, market prices, settlements, P&L, and validation status.

It is designed to show:

- Understanding of trade lifecycle data and reporting questions
- Ability to translate user requirements into SQL and APIs
- Awareness of controls, validation, and safe data access
- Practical full-stack delivery using Python, SQL, React, and Docker
- Clear communication through documentation and realistic examples

## Architecture

```mermaid
flowchart LR
    User[Business / Ops user] --> UI[React + Tailwind dashboard]
    UI --> API[FastAPI routers]
    API --> Generator[AI SQL generation service]
    Generator --> OpenAI[OpenAI API when configured]
    Generator --> Fallback[Deterministic demo fallback]
    API --> Validator[SQL safety validator]
    Validator --> Executor[Query executor]
    Executor --> DB[(PostgreSQL)]
    API --> History[Query history]
    History --> DB
    API --> UI
```

## Tech Stack

- Python, FastAPI, Pydantic
- PostgreSQL
- SQLAlchemy ORM
- OpenAI API
- React, Vite, Tailwind CSS
- Docker Compose
- pytest

## Features

- Capital-markets dataset for instruments, trades, counterparties, books, portfolios, market prices, settlements, users, and query history
- Natural-language question interface
- Generated SQL shown in a readable code block
- Result table with query output
- Query history panel
- Sample capital-markets questions
- Responsive dark dashboard UI
- OpenAI-backed SQL generation when `OPENAI_API_KEY` is set
- Reliable fallback for common demo questions when no API key is available
- Read-only SQL validation with table whitelist and automatic `LIMIT 100`

## Screenshots

Place updated screenshots in:

```text
screenshots/desktop-chat.png
screenshots/mobile-chat.png
```

## Database Model

Core tables:

- `instruments`
- `trades`
- `counterparties`
- `books`
- `portfolios`
- `market_prices`
- `settlements`
- `users`
- `query_history`

## Example Questions

- Show trades pending validation
- Show failed settlements this week
- Show P&L by book
- Show top 5 counterparties by exposure
- Show trades by instrument
- Show market value by portfolio
- Show trades booked today
- Show settlement status by counterparty

## API Endpoints

- `GET /health`
- `GET /schema`
- `GET /sample-questions`
- `POST /ask`
- `GET /query-history`

Backward-compatible endpoints are also available:

- `POST /api/query`
- `GET /api/history`

## Setup

### 1. Start PostgreSQL

```bash
docker compose up -d
```

The container loads `database/schema.sql` and `database/seed.sql` on first startup.

### 2. Configure Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set `OPENAI_API_KEY` in `backend/.env` if you want live AI SQL generation. The demo fallback works without a key.

### 3. Reseed Demo Data

```bash
cd backend
python scripts/seed.py
```

The seed script recreates the capital-markets schema and reloads demo data.

### 4. Run Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend: `http://localhost:8000`

### 5. Run Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend: `http://localhost:5173`

The Vite dev server proxies `/ask`, `/query-history`, `/schema`, `/health`, and `/sample-questions` to the backend.

## Environment Variables

Backend:

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/enterprise_copilot
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
ALLOWED_ORIGINS=http://localhost:5173
```

Frontend:

```text
VITE_API_BASE_URL=
```

Leave `VITE_API_BASE_URL` empty for local Vite proxying. Set it only when calling a separately hosted backend.

## SQL Safety Design

The backend validates generated SQL before execution:

- Allows only `SELECT`
- Rejects multiple statements
- Blocks `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, and `REVOKE`
- Rejects comments and suspicious patterns
- Enforces a whitelist of capital-markets tables
- Automatically appends `LIMIT 100` when no limit is present
- Returns clear validation errors

## Tests

```bash
cd backend
pytest
```

Current coverage includes:

- SQL validator safety rules
- Health endpoint
- Schema endpoint
- Sample questions endpoint

## Engineering Notes

- How the schema maps to trade lifecycle concepts: booking, validation, market value, P&L, settlement, and counterparty exposure
- Why generated SQL must be validated even when produced by an AI model
- How table whitelisting and read-only validation reduce operational risk
- How the backend separates routes, schemas, models, and services
- How a similar assistant could support trade support, operations, risk, or production support analysts
- What would be needed for production: authentication, RBAC, row-level security, schema introspection, audit logging, and model evaluation

## Future Improvements

- Alembic migrations
- Role-based access control and row-level permissions
- Streaming responses
- Chart visualizations for P&L and exposure
- SQL-generation evaluation suite
- Saved dashboards and bookmarked queries
- Real schema introspection instead of static prompt context
- Deployment to a cloud database and container platform
