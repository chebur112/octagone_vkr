import asyncio

import httpx

from app.config import settings


class OneCError(Exception):
    """1С недоступна или ответила не JSON. Ошибки самого запроса приходят в ответе с ok=false."""


class OneCClient:
    def __init__(self) -> None:
        self._http = httpx.AsyncClient(
            base_url=settings.unf_base_url,
            auth=(settings.unf_user, settings.unf_password),
            timeout=60,
            trust_env=False,
            headers={"Connection": "close"},
        )
        self._lock = asyncio.Lock()

    async def _call(self, method: str, path: str, body: dict | None = None) -> dict:
        async with self._lock:
            try:
                response = await self._http.request(method, path, json=body)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError) as e:
                raise OneCError(f"{method} {path}: {e}") from e

    async def metadata(self) -> list[dict]:
        return (await self._call("GET", "/metadata"))["objects"]

    async def lookup(self, catalog: str, text: str) -> dict:
        return await self._call("POST", "/lookup", {"catalog": catalog, "text": text})

    async def query(self, text: str, params: dict | None = None) -> dict:
        return await self._call("POST", "/query", {"text": text, "params": params or {}})

    async def close(self) -> None:
        await self._http.aclose()
