from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.sql_validator import validate_read_only_sql


def _serialize(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


class QueryExecutor:
    def execute(self, db: Session, sql: str) -> tuple[list[str], list[dict[str, Any]]]:
        safe_sql = validate_read_only_sql(sql)
        result = db.execute(text(safe_sql))
        columns = list(result.keys())
        rows = [
            {column: _serialize(value) for column, value in zip(columns, row, strict=True)}
            for row in result.fetchall()
        ]
        return columns, rows
