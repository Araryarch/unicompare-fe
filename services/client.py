import requests
from typing import Optional

BASE_URL = "https://unicompare-be.vercel.app/api"
TIMEOUT = 15

_session = requests.Session()


class DummyResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text
    def json(self):
        return {"error": self.text, "detail": self.text, "message": self.text}

def _safe_request(method, path, **kwargs):
    try:
        kwargs["timeout"] = TIMEOUT
        if method == "GET":
            return _session.get(f"{BASE_URL}{path}", **kwargs)
        elif method == "POST":
            return _session.post(f"{BASE_URL}{path}", **kwargs)
        elif method == "PUT":
            return _session.put(f"{BASE_URL}{path}", **kwargs)
        elif method == "DELETE":
            return _session.delete(f"{BASE_URL}{path}", **kwargs)
    except requests.exceptions.Timeout:
        return DummyResponse(504, "Connection timed out. The server took too long to respond.")
    except requests.exceptions.ConnectionError:
        return DummyResponse(503, "Connection error. Please check your internet or try again later.")
    except requests.exceptions.RequestException as e:
        return DummyResponse(500, f"Network error: {str(e)}")

def api_get(path: str, token: Optional[str] = None, params: Optional[dict] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _safe_request("GET", path, headers=headers, params=params)


def api_post(path: str, token: Optional[str] = None, json: Optional[dict] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _safe_request("POST", path, headers=headers, json=json)


def api_put(path: str, token: Optional[str] = None, json: Optional[dict] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _safe_request("PUT", path, headers=headers, json=json)


def api_delete(path: str, token: Optional[str] = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _safe_request("DELETE", path, headers=headers)
