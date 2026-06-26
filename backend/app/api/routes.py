import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import QueryHistory
from app.schemas.agent import AgentAskRequest, AgentResponse
from app.schemas.query import HistoryItem, QueryRequest, QueryResponse, SchemaResponse
from app.services.answer_builder import build_answer
from app.services.query_executor import QueryExecutor
from app.services.schema_context import SCHEMA_CONTEXT, TABLES
from app.services.sql_generator import SAMPLE_QUESTIONS, SQLGenerator
from app.services.sql_validator import UnsafeQueryError
from app.services.trade_ops_agent import TRADE_OPS_SAMPLE_QUESTIONS, TradeOpsAgent
from app.services.trade_ops_client import TradeOpsClientError

logger = logging.getLogger(__name__)

router = APIRouter()
sql_generator = SQLGenerator()
query_executor = QueryExecutor()
trade_ops_agent = TradeOpsAgent()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "trade-operations-copilot"}


@router.get("/schema", response_model=SchemaResponse)
def get_schema() -> SchemaResponse:
    return SchemaResponse(tables=TABLES, schema_context=SCHEMA_CONTEXT)


@router.get("/sample-questions", response_model=list[str])
def get_sample_questions() -> list[str]:
    return SAMPLE_QUESTIONS


@router.get("/agent/sample-questions", response_model=list[str])
def get_agent_sample_questions() -> list[str]:
    return TRADE_OPS_SAMPLE_QUESTIONS


@router.post("/agent/ask", response_model=AgentResponse)
def ask_agent(payload: AgentAskRequest) -> AgentResponse:
    try:
        return trade_ops_agent.answer(payload.question)
    except TradeOpsClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Trade operations agent failed")
        raise HTTPException(status_code=500, detail="Unable to process the copilot question.") from exc


@router.post("/ask", response_model=QueryResponse)
def ask(payload: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    try:
        sql, answer_hint = sql_generator.generate(payload.question)
        columns, rows = query_executor.execute(db, sql)
        answer = build_answer(answer_hint, rows)

        db.add(
            QueryHistory(
                question=payload.question,
                generated_sql=sql,
                answer=answer,
                row_count=len(rows),
            )
        )
        db.commit()

        return QueryResponse(
            question=payload.question,
            answer=answer,
            sql=sql,
            columns=columns,
            rows=rows,
            row_count=len(rows),
        )
    except UnsafeQueryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database query failed")
        raise HTTPException(status_code=500, detail="Database query failed.") from exc
    except Exception as exc:
        db.rollback()
        logger.exception("Unable to process question")
        raise HTTPException(status_code=500, detail="Unable to process the question.") from exc


@router.get("/query-history", response_model=list[HistoryItem])
def query_history(db: Session = Depends(get_db)) -> list[QueryHistory]:
    statement = select(QueryHistory).order_by(QueryHistory.created_at.desc()).limit(25)
    return list(db.scalars(statement))


# Backward-compatible routes for the first version of the app and older frontend builds.
@router.post("/api/query", response_model=QueryResponse)
def legacy_query(payload: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    return ask(payload, db)


@router.get("/api/history", response_model=list[HistoryItem])
def legacy_history(db: Session = Depends(get_db)) -> list[QueryHistory]:
    return query_history(db)
