import re

from app.services.schema_context import ALLOWED_TABLES


class UnsafeQueryError(ValueError):
    pass


BLOCKED_KEYWORDS = {
    "alter",
    "create",
    "delete",
    "drop",
    "grant",
    "insert",
    "revoke",
    "truncate",
    "update",
}
SUSPICIOUS_PATTERNS = [
    r"--",
    r"/\*",
    r"\*/",
    r"\bpg_",
    r"\binformation_schema\b",
    r"\bcurrent_setting\b",
    r"\bload_file\b",
]


def validate_read_only_sql(sql: str) -> str:
    normalized = " ".join(sql.strip().strip("`").rstrip(";").split())
    lowered = normalized.lower()

    if not normalized:
        raise UnsafeQueryError("SQL cannot be empty.")

    if ";" in normalized:
        raise UnsafeQueryError("Multiple SQL statements are not allowed.")

    if not lowered.startswith("select "):
        raise UnsafeQueryError("Only SELECT queries are allowed.")

    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, lowered):
            raise UnsafeQueryError("Comments and suspicious SQL patterns are not allowed.")

    tokens = set(re.findall(r"[a-z_]+", lowered))
    blocked = sorted(tokens.intersection(BLOCKED_KEYWORDS))
    if blocked:
        raise UnsafeQueryError(f"Blocked SQL keyword: {blocked[0].upper()}.")

    referenced_tables = _extract_referenced_tables(lowered)
    unknown_tables = sorted(referenced_tables - ALLOWED_TABLES)
    if unknown_tables:
        raise UnsafeQueryError(
            "Query references a table outside the allowed capital markets schema: "
            f"{', '.join(unknown_tables)}."
        )

    return _add_default_limit(normalized)


def _extract_referenced_tables(sql: str) -> set[str]:
    matches = re.findall(r"\b(?:from|join)\s+([a-z_][a-z0-9_\.]*)", sql)
    tables = set()
    for match in matches:
        if match.startswith("("):
            continue
        tables.add(match.split(".")[-1])
    return tables


def _add_default_limit(sql: str) -> str:
    if re.search(r"\blimit\s+\d+\b", sql, flags=re.IGNORECASE):
        return sql
    return f"{sql} LIMIT 100"
