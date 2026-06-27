import logging
from time import perf_counter

from fastapi import APIRouter, HTTPException

from app.schemas.agent import AgentAskRequest, AgentResponse
from app.services.intent_classifier import IntentClassifier
from app.services.trade_ops_agent import TRADE_OPS_SAMPLE_QUESTIONS, TradeOpsAgent
from app.services.trade_ops_client import TradeOpsClientError

logger = logging.getLogger(__name__)

router = APIRouter()
trade_ops_agent = TradeOpsAgent()
intent_classifier = IntentClassifier()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "trade-operations-copilot"}


@router.get("/agent/sample-questions", response_model=list[str])
def get_agent_sample_questions() -> list[str]:
    return TRADE_OPS_SAMPLE_QUESTIONS


@router.post("/agent/ask", response_model=AgentResponse)
def ask_agent(payload: AgentAskRequest) -> AgentResponse:
    started_at = perf_counter()
    try:
        response = trade_ops_agent.answer(payload.question)
        response_time_ms = _elapsed_ms(started_at)
        _record_agent_log(payload.question, response, response_time_ms)
        return response
    except TradeOpsClientError as exc:
        _record_agent_error(payload.question, str(exc), _elapsed_ms(started_at))
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Trade operations agent failed")
        _record_agent_error(payload.question, str(exc), _elapsed_ms(started_at))
        raise HTTPException(status_code=500, detail="Unable to process the copilot question.") from exc


def _record_agent_log(
    question: str,
    response: AgentResponse,
    response_time_ms: int,
) -> None:
    endpoints = ", ".join(source.endpoint for source in response.sources) or None
    payload = {
        "question": question,
        "intent": response.intent,
        "answer": response.answer,
        "data_source_endpoint": endpoints,
        "row_count": response.row_count,
        "error": response.error,
        "success": response.error is None,
        "response_time_ms": response_time_ms,
        "model": response.model,
        "tokens_used": response.tokens_used,
    }
    try:
        trade_ops_agent.client.post("/api/ai-copilot/logs", payload)
    except TradeOpsClientError:
        logger.exception("Unable to persist AI Copilot interaction log")


def _record_agent_error(question: str, error: str, response_time_ms: int) -> None:
    payload = {
        "question": question,
        "intent": intent_classifier.classify(question).value,
        "answer": None,
        "data_source_endpoint": None,
        "row_count": 0,
        "error": error,
        "success": False,
        "response_time_ms": response_time_ms,
        "model": None,
        "tokens_used": None,
    }
    try:
        trade_ops_agent.client.post("/api/ai-copilot/logs", payload)
    except TradeOpsClientError:
        logger.exception("Unable to persist failed AI Copilot interaction log")


def _elapsed_ms(started_at: float) -> int:
    return max(0, round((perf_counter() - started_at) * 1000))
