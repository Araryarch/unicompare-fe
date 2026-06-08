from typing import Optional
from services.client import api_get, api_post, api_put, api_delete
import streamlit as st


def fetch_universities():
    res = api_get("/universities")
    if res.status_code == 200:
        return res.json().get("universities", [])
    return []


@st.cache_data
def search_universities(query: str):
    res = api_get("/universities/search", params={"q": query})
    if res.status_code == 200:
        return res.json()
    return []


def fetch_programs(uni_id: str):
    if not uni_id:
        return []
    res = api_get(f"/universities/{uni_id}")
    if res.status_code == 200:
        return res.json().get("programs", [])
    return []


def compare_by_score(score: float):
    res = api_get("/compare", params={"score": score})
    if res.status_code == 200:
        data = res.json()
        if isinstance(data, dict):
            return data.get("universities", [])
        return data if isinstance(data, list) else []
    return None


def create_university(token: Optional[str], uni_id: str, name: str, sources: list[str]):
    res = api_post("/admin/universities", token=token,
                   json={"id": uni_id, "name": name, "sources": sources})
    return res.status_code == 200, res.text if res.status_code != 200 else None


def update_university(token: Optional[str], uni_id: str, name: Optional[str]):
    res = api_put(f"/admin/universities/{uni_id}", token=token,
                  json={"name": name})
    return res.status_code == 200, res.text if res.status_code != 200 else None


def delete_university(token: Optional[str], uni_id: str):
    res = api_delete(f"/admin/universities/{uni_id}", token=token)
    return res.status_code == 200, res.text if res.status_code != 200 else None


def update_programs(token: Optional[str], uni_id: str, programs: list[dict]):
    res = api_put(f"/admin/universities/{uni_id}/programs", token=token,
                  json={"programs": programs})
    return res.status_code == 200, res.text if res.status_code != 200 else None


def list_users(token: Optional[str]):
    res = api_get("/admin/users", token=token)
    if res.status_code == 200:
        return res.json()
    return None
