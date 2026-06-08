from typing import Optional
from services.client import api_post, api_get


def login(username: str, password: str):
    res = api_post("/auth/login", json={"username": username, "password": password})
    if res.status_code == 200:
        return res.json().get("access_token")
    return None


def register(username: str, password: str):
    res = api_post("/auth/register", json={"username": username, "password": password})
    return res.status_code == 200, res.text if res.status_code != 200 else None


def get_profile(token: Optional[str]):
    try:
        res = api_get("/auth/me", token=token)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 401:
            return "UNAUTHORIZED"
        return None
    except Exception:
        return None
