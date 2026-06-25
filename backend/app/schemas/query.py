from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class QueryResponse(BaseModel):
    question: str
    answer: str
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int


class HistoryItem(BaseModel):
    id: int
    question: str
    generated_sql: str
    answer: str
    row_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TableInfo(BaseModel):
    name: str
    columns: list[str]
    description: str


class SchemaResponse(BaseModel):
    tables: list[TableInfo]
    schema_context: str
