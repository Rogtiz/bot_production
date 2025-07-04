import os
import httpx
from typing import Optional

from config import settings

API_BASE_URL = settings.API_URL  # имя контейнера из docker-compose

client = httpx.AsyncClient(base_url=API_BASE_URL)

# --- USER ---
async def get_user_by_chat_id(chat_id: str) -> Optional[dict]:
    try:
        response = await client.get(f"/bot/user/{chat_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise

async def create_user(chat_id: str, username: str) -> Optional[dict]:
    payload = {"chat_id": chat_id, "username": username}
    response = await client.post("/bot/user", json=payload)
    response.raise_for_status()
    return response.json()


async def create_group(name: str, chat_id: str) -> Optional[dict]:
    payload = {"name": name, "chat_id": chat_id}
    response = await client.post("/bot/group", json=payload)
    response.raise_for_status()
    return response.json()

# --- FEEDBACK ---
async def create_feedback(chat_id: str, content: str) -> dict:
    payload = {"chat_id": chat_id, "message": content}
    response = await client.post("/bot/feedback", json=payload)
    response.raise_for_status()
    return response.json()


async def get_feedback() -> Optional[list[dict]]:
    try:
        response = await client.get(f"/bot/feedback")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise

# --- PROPERTY ---
async def get_property(key: str) -> Optional[dict]:
    try:
        response = await client.get(f"/bot/property/{key}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def update_property(key: str, value: str) -> dict:
    response = await client.put(f"/bot/property/{key}?value={value}")
    response.raise_for_status()
    return response.json()


async def get_top_players(page: int) -> Optional[list[dict]]:
    try:
        resp = await client.get("/gwent/get_top_players", params={"page": page})
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_mmr_threshold_of_ranks() -> Optional[list[dict]]:
    try:
        resp = await client.get("/gwent/get_threshold_of_ranks")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_username_by_place(place: int) -> Optional[dict]:
    try:
        resp = await client.get(f"/gwent/get_username_by_place/{place}")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_player_id(username: str) -> Optional[dict]:
    try:
        resp = await client.get(f"/gwent/user/{username}/id")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_profile_image(username: str) -> Optional[dict]:
    try:
        resp = await client.get(f"/gwent/user/{username}/profile_image")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_player_ranking(user_id: str) -> Optional[dict]:
    try:
        resp = await client.get(f"/gwent/user/{user_id}/ranking")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_player_profile_data(user_id: str) -> Optional[dict]:
    try:
        resp = await client.get(f"/gwent/user/{user_id}/profile")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def get_player_deck(user_id: str) -> Optional[dict]:
    try:
        resp = await client.get(f"/gwent/user/{user_id}/deck")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise