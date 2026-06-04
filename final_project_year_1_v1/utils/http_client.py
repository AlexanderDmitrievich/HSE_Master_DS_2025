import os

import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")


def api_get(path: str, **kwargs) -> requests.Response:
    return requests.get(f"{API_URL}{path}", timeout=30, **kwargs)


def api_post(path: str, **kwargs) -> requests.Response:
    return requests.post(f"{API_URL}{path}", timeout=30, **kwargs)


def parse_response(response: requests.Response) -> tuple[dict | list | None, str | None]:
    if response.ok:
        return response.json(), None
    try:
        payload = response.json()
        detail = payload.get("detail", payload)
    except Exception:
        detail = response.text
    return None, str(detail)
