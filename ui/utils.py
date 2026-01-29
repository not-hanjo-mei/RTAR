import httpx

API_BASE = "http://localhost:7860/api/v1"


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
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(f"{API_BASE}{path}")
        return _handle_response(response)


async def api_post(path: str, data: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{API_BASE}{path}", json=data or {})
        return _handle_response(response)


async def api_put(path: str, data: dict) -> dict:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.put(f"{API_BASE}{path}", json=data)
        return _handle_response(response)


async def api_delete(path: str) -> dict:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.delete(f"{API_BASE}{path}")
        return _handle_response(response)
