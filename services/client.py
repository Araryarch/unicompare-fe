import requests
from typing import Optional

BASE_URL = "https://unicompare-be.vercel.app/api"
TIMEOUT = 15

_session = requests.Session()


def api_get(path: str, token: Optional[str] = None, params: Optional[dict] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _session.get(f"{BASE_URL}{path}", headers=headers, params=params, timeout=TIMEOUT)


def api_post(path: str, token: Optional[str] = None, json: Optional[dict] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _session.post(f"{BASE_URL}{path}", headers=headers, json=json, timeout=TIMEOUT)


def api_put(path: str, token: Optional[str] = None, json: Optional[dict] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _session.put(f"{BASE_URL}{path}", headers=headers, json=json, timeout=TIMEOUT)


def api_delete(path: str, token: Optional[str] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _session.delete(f"{BASE_URL}{path}", headers=headers, timeout=TIMEOUT)
