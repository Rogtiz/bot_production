import json
from fastapi import APIRouter, Depends, HTTPException
from app.gwent.utils import GwentAPI, GwentProfileParser, GwentSiteParser
from app.gwent.schemas import FullUserRankingInfoSchema, FullProfileDataSchema, GwentSitePlayerInfoSchema, RanksThresholdSchema, FullDeckInfoSchema, ProfileImageSchema
from app.gwent.dao import PlayersDAO
from app.bot.dao import PropertiesDAO

from app.redis import redis_cache, redis_client

router = APIRouter()

api = GwentAPI()
profile_parser = GwentProfileParser()
site_parser = GwentSiteParser()

@router.get("/user/{username}/id")
async def get_user_id(username: str):
    is_existing = await PlayersDAO.find_one_or_none(nickname=username)
    if is_existing:
        return {"user_id": is_existing.gwent_id}
    user_id = await api.get_user_id(username)
    if user_id:
        is_existing = await PlayersDAO.find_one_or_none(gwent_id=user_id)
        if is_existing:
            await PlayersDAO.update(model_id=is_existing.id, nickname=username)
        else:
            await PlayersDAO.add(nickname=username, gwent_id=user_id)
        return {"user_id": user_id}
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/user/{user_id}/ranking")
@redis_cache(schema=FullUserRankingInfoSchema, key_func=lambda user_id: f"ranking_info:{user_id}", expire=1800)
async def get_ranking_info(user_id: str) -> FullUserRankingInfoSchema:
    property = await PropertiesDAO.find_one_or_none(name="season_id")
    if not property:
        raise HTTPException(status_code=579)
    season_id = property.value
    ranking_info = await api.get_ranking_info(user_id, season_id)
    if ranking_info:
        # if ranking_info.get("error"):
        #     raise HTTPException(status_code=484, detail="Player hasn't played this season")
        return ranking_info
    raise HTTPException(status_code=404, detail="Ranking information not found")


@router.get("/user/{username}/profile_image")
@redis_cache(schema=ProfileImageSchema, key_func=lambda username: f"profile_image:{username}", expire=600)
async def get_profile_page(username: str) -> ProfileImageSchema:
    profile_image = await api.get_profile_image(username)
    if profile_image:
        return profile_image
    raise HTTPException(status_code=404, detail="Profile information not found")


@router.get("/user/{user_id}/profile")
@redis_cache(schema=FullProfileDataSchema, key_func=lambda user_id: f"profile_data:{user_id}", expire=1800)
async def get_profile_data(user_id: str) -> FullProfileDataSchema:
    profile_data = await api.get_profile_data(user_id)
    if profile_data:
        # return profile_parser.format_collection(profile_data.get("username"), profile_data)
        return profile_data
    raise HTTPException(status_code=404, detail="Profile data not found")


@router.get("/user/{user_id}/deck")
@redis_cache(schema=FullDeckInfoSchema, key_func=lambda user_id: f"deck_info:{user_id}", expire=1800)
async def get_deck_info(user_id: str) -> FullDeckInfoSchema:
    deck_info = await api.get_card_collection(user_id)
    if deck_info:
        return deck_info
    raise HTTPException(status_code=404, detail="Deck data not found")


@router.get("/get_threshold_of_ranks")
@redis_cache(schema=RanksThresholdSchema, key_func=lambda: "ranks_threshold", expire=36000)
async def get_threshold_of_ranks() -> RanksThresholdSchema:
    thresholds = site_parser.get_mmr_threshold_of_ranks()
    if thresholds:
        return thresholds
    raise HTTPException(status_code=404, detail="Thresholds not found")


@router.get("/get_username_by_place/{place}")
@redis_cache(schema=GwentSitePlayerInfoSchema, key_func=lambda place: f"site_info:{place}", expire=3600)
async def get_username_by_place(place: int) -> GwentSitePlayerInfoSchema:
    username = site_parser.get_mmr_threshold(place)
    if username:
        return username
    raise HTTPException(status_code=404, detail="Username not found")

#  -> list[GwentSitePlayerInfoSchema]

@router.get("/get_top_players")
async def get_top_players(page: int = 1):
    cached = await redis_client.get(f"top_players:{page}")
    if cached:
        print("Cache")
        return json.loads(cached)
    top_players = site_parser.get_top_ranks(page)
    if top_players:
        print("Not cache")
        await redis_client.set(f"top_players:{page}", json.dumps(top_players), ex=3600)
        return top_players
    raise HTTPException(status_code=404, detail="Top players not found")
