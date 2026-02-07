import os

import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE = f"http://localhost:{os.getenv('RTAR_PORT', '42069')}/api/v1"

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url=API_BASE,
            timeout=60.0,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
    return _client


async def close_client() -> None:
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


class APIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API error {status_code}: {detail}")


def _handle_response(response: httpx.Response) -> dict:
    if response.status_code >= 400:
        try:
            error_data = response.json()
            detail = error_data.get("detail", response.text)
        except Exception:
            detail = response.text or f"HTTP {response.status_code}"
        raise APIError(response.status_code, detail)

    if not response.content:
        return {}
    return response.json()


async def api_get(path: str) -> dict:
    client = _get_client()
    response = await client.get(path)
    return _handle_response(response)


async def api_post(path: str, data: dict | None = None) -> dict:
    client = _get_client()
    response = await client.post(path, json=data or {})
    return _handle_response(response)


async def api_put(path: str, data: dict) -> dict:
    client = _get_client()
    response = await client.put(path, json=data)
    return _handle_response(response)


async def api_delete(path: str) -> dict:
    client = _get_client()
    response = await client.delete(path)
    return _handle_response(response)
