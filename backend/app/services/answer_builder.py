from typing import Any


def build_answer(hint: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return f"{hint} No matching rows were found."

    if len(rows) == 1 and len(rows[0]) == 1:
        column, value = next(iter(rows[0].items()))
        label = column.replace("_", " ")
        return f"{hint} {label.capitalize()}: {value}."

    return f"{hint} Found {len(rows)} matching row{'s' if len(rows) != 1 else ''}."
