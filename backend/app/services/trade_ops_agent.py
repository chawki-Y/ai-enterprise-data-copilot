from __future__ import annotations

from datetime import date
import re
from typing import Any

from openai import OpenAI

from app.config import get_settings
from app.schemas.agent import AgentResponse, AgentSource
from app.services.trade_ops_client import TradeOpsClient


TRADE_OPS_SAMPLE_QUESTIONS = [
    "Give me an operations morning summary.",
    "Show me today's rejected trades.",
    "Why was trade TRD-20260625-000004 rejected?",
    "Summarize audit logs for trade TRD-20260625-000004.",
    "Is any market data stale?",
    "What happened with AAPL market price?",
    "Summarize today's P&L.",
    "Highlight operational risks.",
]


class TradeOpsAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = TradeOpsClient()
        self.openai = OpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    def answer(self, question: str) -> AgentResponse:
        normalized = question.lower().strip()
        trade_id = self._extract_trade_id(question)

        if trade_id and ("why" in normalized or "reject" in normalized or "investigat" in normalized):
            return self._answer_trade_investigation(question, trade_id)

        if trade_id and "audit" in normalized:
            return self._answer_trade_audit(question, trade_id)

        if "rejected" in normalized or "rejection" in normalized:
            return self._answer_rejected_trades(question)

        if "stale" in normalized or "market data" in normalized and "any" in normalized:
            return self._answer_market_data_health(question)

        if "market price" in normalized or "price" in normalized:
            return self._answer_market_price(question)

        if "p&l" in normalized or "pnl" in normalized:
            return self._answer_pnl(question)

        if "risk" in normalized or "summary" in normalized or "morning" in normalized or "status" in normalized:
            return self._answer_operations_summary(question)

        return self._answer_operations_summary(question)

    def _answer_operations_summary(self, question: str) -> AgentResponse:
        summary = self.client.get("/api/operations/summary")
        report = self.client.get("/api/trades/report")
        risks = self._build_risk_points(summary)
        answer = (
            f"Operations snapshot: {summary.get('bookedTradesToday', 0)} trades booked today, "
            f"{summary.get('rejectedTradesToday', 0)} rejected today, "
            f"total P&L today {self._money(summary.get('totalPnLToday', 0))}. "
            f"Market data shows {summary.get('staleMarketDataCount', 0)} stale and "
            f"{summary.get('unavailableMarketDataCount', 0)} unavailable instruments."
        )
        if risks:
            answer += " Key risks: " + " ".join(risks)

        return self._maybe_enhance(
            question=question,
            intent="operations_summary",
            answer=answer,
            data={"summary": summary, "report": report},
            sources=[
                AgentSource(label="Operations summary", endpoint="/api/operations/summary"),
                AgentSource(label="Trade report", endpoint="/api/trades/report"),
            ],
            suggestions=[
                "Show me today's rejected trades.",
                "Is any market data stale?",
                "Summarize today's P&L.",
            ],
        )

    def _answer_rejected_trades(self, question: str) -> AgentResponse:
        trades = self.client.get("/api/trades")
        today = date.today().isoformat()
        rejected = [
            trade
            for trade in trades
            if trade.get("Status") == "REJECTED" and str(trade.get("TradeDate", "")).startswith(today)
        ]
        if not rejected:
            rejected = [trade for trade in trades if trade.get("Status") == "REJECTED"]

        answer = f"Found {len(rejected)} rejected trade{'s' if len(rejected) != 1 else ''}."
        if rejected:
            top = rejected[0]
            answer += (
                f" Latest: {top.get('TradeId')} on {top.get('Instrument')} was rejected because "
                f"{top.get('RejectionReason') or 'it failed validation'}."
            )

        return self._maybe_enhance(
            question=question,
            intent="rejected_trades",
            answer=answer,
            data=rejected,
            sources=[AgentSource(label="Trades", endpoint="/api/trades")],
            suggestions=[
                "Summarize audit logs for this trade.",
                "Give me an operations morning summary.",
            ],
        )

    def _answer_trade_investigation(self, question: str, trade_id: str) -> AgentResponse:
        investigation = self.client.get(f"/api/operations/investigate/{trade_id}")
        trade = investigation.get("trade", {})
        audit_logs = investigation.get("auditLogs", [])
        answer = investigation.get("summary") or f"Trade {trade_id} investigation loaded."
        if trade.get("Status") == "REJECTED":
            answer += f" Rejection reason: {trade.get('RejectionReason') or 'not specified'}."
        answer += f" Found {len(audit_logs)} related audit event{'s' if len(audit_logs) != 1 else ''}."

        return self._maybe_enhance(
            question=question,
            intent="trade_investigation",
            answer=answer,
            data=investigation,
            sources=[AgentSource(label="Trade investigation", endpoint=f"/api/operations/investigate/{trade_id}")],
            suggestions=[
                "Summarize today's P&L.",
                "Show me today's rejected trades.",
            ],
        )

    def _answer_trade_audit(self, question: str, trade_id: str) -> AgentResponse:
        investigation = self.client.get(f"/api/operations/investigate/{trade_id}")
        logs = investigation.get("auditLogs", [])
        if logs:
            answer = f"Trade {trade_id} has {len(logs)} audit event{'s' if len(logs) != 1 else ''}. Latest event: {logs[0].get('description')}."
        else:
            answer = f"No audit events were found for trade {trade_id}."

        return self._maybe_enhance(
            question=question,
            intent="trade_audit",
            answer=answer,
            data=logs,
            sources=[AgentSource(label="Trade investigation", endpoint=f"/api/operations/investigate/{trade_id}")],
            suggestions=["Why was this trade rejected?", "Give me an operations morning summary."],
        )

    def _answer_market_data_health(self, question: str) -> AgentResponse:
        overview = self.client.get("/api/market-overview")
        stale = [item for item in overview if item.get("stale") or item.get("fromDatabase") or item.get("marketPrice") is None]
        answer = f"Market overview contains {len(stale)} stale, fallback, or unavailable instrument{'s' if len(stale) != 1 else ''}."
        if stale:
            names = ", ".join(str(item.get("symbol")) for item in stale[:5])
            answer += f" Review: {names}."

        return self._maybe_enhance(
            question=question,
            intent="market_data_health",
            answer=answer,
            data=stale,
            sources=[AgentSource(label="Market overview", endpoint="/api/market-overview")],
            suggestions=[
                "What happened with AAPL market price?",
                "Highlight operational risks.",
            ],
        )

    def _answer_market_price(self, question: str) -> AgentResponse:
        symbol = self._extract_symbol(question)
        if not symbol:
            return self._answer_market_data_health(question)

        market_data = self.client.get(f"/api/market-price/{symbol}")
        source = market_data.get("source") or "unknown"
        freshness = market_data.get("freshnessLabel") or "freshness unavailable"
        answer = (
            f"{symbol} market price is {market_data.get('marketPrice')} from {source}. "
            f"Freshness: {freshness}."
        )
        if market_data.get("fromCache"):
            answer += " The value came from the in-memory cache."
        if market_data.get("fromDatabase"):
            answer += " The value came from the database fallback."
        if market_data.get("stale"):
            answer += " The value is marked stale."

        return self._maybe_enhance(
            question=question,
            intent="market_price",
            answer=answer,
            data=market_data,
            sources=[AgentSource(label="Market price", endpoint=f"/api/market-price/{symbol}")],
            suggestions=[
                "Is any market data stale?",
                "Give me an operations morning summary.",
            ],
        )

    def _answer_pnl(self, question: str) -> AgentResponse:
        report = self.client.get("/api/trades/report")
        summary = self.client.get("/api/operations/summary")
        answer = (
            f"Total booked-trade P&L is {self._money(report.get('TotalPnL', 0))}. "
            f"Today's booked-trade P&L is {self._money(summary.get('totalPnLToday', 0))}."
        )

        return self._maybe_enhance(
            question=question,
            intent="pnl_summary",
            answer=answer,
            data={"report": report, "summary": summary},
            sources=[
                AgentSource(label="Trade report", endpoint="/api/trades/report"),
                AgentSource(label="Operations summary", endpoint="/api/operations/summary"),
            ],
            suggestions=[
                "Show me today's rejected trades.",
                "Highlight operational risks.",
            ],
        )

    def _maybe_enhance(
        self,
        question: str,
        intent: str,
        answer: str,
        data: Any,
        sources: list[AgentSource],
        suggestions: list[str],
    ) -> AgentResponse:
        if not self.openai:
            return AgentResponse(
                question=question,
                intent=intent,
                answer=answer,
                data=data,
                sources=sources,
                suggestions=suggestions,
            )

        prompt = (
            "Rewrite the answer for a middle-office operations analyst. "
            "Be concise, factual, and do not invent data.\n\n"
            f"Question: {question}\n"
            f"Draft answer: {answer}\n"
            f"Data: {data}"
        )
        response = self.openai.chat.completions.create(
            model=self.settings.openai_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are a trade operations copilot."},
                {"role": "user", "content": prompt},
            ],
        )
        enhanced = response.choices[0].message.content or answer
        return AgentResponse(
            question=question,
            intent=intent,
            answer=enhanced,
            data=data,
            sources=sources,
            suggestions=suggestions,
        )

    @staticmethod
    def _extract_trade_id(text: str) -> str | None:
        match = re.search(r"\bTRD-\d{8}-\d{6}\b", text.upper())
        return match.group(0) if match else None

    @staticmethod
    def _extract_symbol(text: str) -> str | None:
        candidates = re.findall(r"\b[A-Z]{1,5}(?:/[A-Z]{3})?\b", text.upper())
        ignored = {"WHAT", "WHY", "SHOW", "GIVE", "TODAY", "PRICE", "MARKET", "DATA", "PNL"}
        for candidate in candidates:
            if candidate not in ignored and not candidate.startswith("TRD"):
                return candidate
        return None

    @staticmethod
    def _money(value: Any) -> str:
        return f"{NumberHelper.to_float(value):,.4f}"

    @staticmethod
    def _build_risk_points(summary: dict[str, Any]) -> list[str]:
        risks = []
        if summary.get("rejectedTradesToday", 0) > 0:
            risks.append(f"{summary['rejectedTradesToday']} rejected trade(s) need review.")
        if summary.get("staleMarketDataCount", 0) > 0:
            risks.append(f"{summary['staleMarketDataCount']} stale market data item(s).")
        if summary.get("unavailableMarketDataCount", 0) > 0:
            risks.append(f"{summary['unavailableMarketDataCount']} unavailable market price(s).")
        if summary.get("failedMarketDataRefreshCount", 0) > 0:
            risks.append(f"{summary['failedMarketDataRefreshCount']} failed market refresh event(s) in 24h.")
        return risks


class NumberHelper:
    @staticmethod
    def to_float(value: Any) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0
