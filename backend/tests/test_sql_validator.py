import pytest

from app.services.sql_validator import UnsafeQueryError, validate_read_only_sql


def test_adds_default_limit() -> None:
    sql = validate_read_only_sql("SELECT trade_id FROM trades ORDER BY trade_id")

    assert sql.endswith("LIMIT 100")


def test_keeps_existing_limit() -> None:
    sql = validate_read_only_sql("SELECT trade_id FROM trades LIMIT 5")

    assert sql == "SELECT trade_id FROM trades LIMIT 5"


@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE trades SET status = 'Validated'",
        "DELETE FROM trades",
        "DROP TABLE trades",
        "SELECT * FROM trades; SELECT * FROM users",
        "SELECT * FROM trades -- hide something",
        "SELECT * FROM information_schema.tables",
    ],
)
def test_rejects_unsafe_sql(sql: str) -> None:
    with pytest.raises(UnsafeQueryError):
        validate_read_only_sql(sql)


def test_rejects_non_whitelisted_table() -> None:
    with pytest.raises(UnsafeQueryError, match="outside the allowed"):
        validate_read_only_sql("SELECT * FROM payroll")
