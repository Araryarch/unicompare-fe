import requests
from typing import Optional

BASE_URL = "https://unicompare-be.vercel.app/api"


def api_get(path: str, token: Optional[str] = None, params: Optional[dict] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.get(f"{BASE_URL}{path}", headers=headers, params=params)


def api_post(path: str, token: Optional[str] = None, json: Optional[dict] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.post(f"{BASE_URL}{path}", headers=headers, json=json)


def api_put(path: str, token: Optional[str] = None, json: Optional[dict] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.put(f"{BASE_URL}{path}", headers=headers, json=json)


def api_delete(path: str, token: Optional[str] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.delete(f"{BASE_URL}{path}", headers=headers)
