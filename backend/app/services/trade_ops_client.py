from typing import Any

import httpx

from app.config import get_settings


class TradeOpsClientError(RuntimeError):
    pass


class TradeOpsClient:
    def __init__(self) -> None:
        self.base_url = get_settings().trade_ops_api_base_url.rstrip("/")

    def get(self, endpoint: str) -> Any:
        return self._request("GET", endpoint)

    def post(self, endpoint: str, payload: dict[str, Any]) -> Any:
        return self._request("POST", endpoint, json=payload)

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            response = httpx.request(method, url, timeout=8, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            message = self._extract_error(exc.response)
            raise TradeOpsClientError(message) from exc
        except httpx.RequestError as exc:
            raise TradeOpsClientError(
                f"Trade Operations API is unavailable at {self.base_url}."
            ) from exc

    @staticmethod
    def _extract_error(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text or "Trade Operations API request failed."

        return payload.get("message") or payload.get("error") or "Trade Operations API request failed."
