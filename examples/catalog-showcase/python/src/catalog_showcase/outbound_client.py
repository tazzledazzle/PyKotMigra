"""Outbound HTTP client (catalog: outbound HTTP client)."""

from __future__ import annotations

import httpx


class DownstreamClient:
    """Thin httpx wrapper — swap base_url via Settings."""

    def __init__(self, base_url: str | None) -> None:
        self._base = (base_url or "").rstrip("/")

    async def fetch_json_placeholder(self, post_id: int = 1) -> dict:
        """Calls jsonplaceholder.typicode.com (no auth) for demo portability."""
        url = f"{self._base}/posts/{post_id}" if self._base else f"https://jsonplaceholder.typicode.com/posts/{post_id}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
