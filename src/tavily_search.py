from __future__ import annotations

import httpx
from typing import Protocol

from config.settings import settings


class SearchClientProtocol(Protocol):
    async def search(self, query: str) -> str:
        ...


class MockTavilySearchClient:
    async def search(self, query: str) -> str:
        return (
            "[Mock Tavily Search Context] "
            "Search results were not requested in this test configuration."
        )


class TavilySearchClient:
    base_url = "https://api.tavily.ai/search"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or settings.tavily_api_key
        self.base_url = base_url or self.base_url

        if not self.api_key:
            raise ValueError("Tavily API key is required for fallback search.")

    async def search(self, query: str) -> str:
        payload = {"query": query}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        if isinstance(data, dict):
            if "context" in data:
                return str(data["context"])
            if "results" in data:
                return str(data["results"])

        return str(data)
