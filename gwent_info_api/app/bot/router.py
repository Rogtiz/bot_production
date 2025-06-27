from fastapi import APIRouter, HTTPException
from app.bot.dao import UsersDAO, PropertiesDAO, FeedbacksDAO, GroupsDAO
from app.bot.schemas import UserSchema, UserCreationSchema, FeedbackSchema, FeedbackCreationSchema, PropertyCreationSchema, GroupSchema, GroupCreationSchema, PropertySchema, UserUpdateSchema
from app.redis import redis_cache, redis_client

import json

router = APIRouter()

@router.get("/user/{chat_id}")
@redis_cache(schema=UserSchema, key_func=lambda chat_id: f"user:{chat_id}", expire=1200)
async def get_user(chat_id: str) -> UserSchema:
    """
    Get user by chat_id.
    """
    user = await UsersDAO.find_one_or_none(chat_id=chat_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/user")
async def create_user(user_data: UserCreationSchema) -> UserSchema:
    """
    Create a new user.
    """
    user = await UsersDAO.add(**user_data.dict())
    if user:
        return user
    raise HTTPException(status_code=400, detail="User not created")


@router.put("/user/{user_id}")
async def update_user(user_id: int, user_data: UserUpdateSchema) -> UserSchema:
    is_existing = await UsersDAO.find_one_or_none(id=user_id)
    if is_existing:
        updated_user = await UsersDAO.update(model_id=user_id, **user_data.dict())
        return updated_user
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/feedback")
async def get_all_feedback() -> list[FeedbackSchema]:
    """
    Get all feedback.
    """
    feedback = await FeedbacksDAO.find_all()
    if feedback:
        return feedback
    raise HTTPException(status_code=404, detail="No feedback found")


@router.post("/feedback")
async def create_feedback(feedback_data: FeedbackCreationSchema) -> FeedbackSchema:
    """
    Create a new feedback.
    """
    user_id = await UsersDAO.find_one_or_none(chat_id=feedback_data.chat_id)
    if user_id:
        user_id = user_id.id
    feedback = await FeedbacksDAO.add(user_id=user_id, **feedback_data.dict())
    if feedback:
        return feedback
    raise HTTPException(status_code=400, detail="Feedback not created")


@router.get("/property/{key}")
@redis_cache(schema=PropertySchema)
async def get_property(key: str) -> PropertySchema:
    """
    Get a property by key.
    """
    # cached_value = await redis_client.get(key)
    # if cached_value:
    #     return PropertySchema(**json.loads(cached_value))
    property_value = await PropertiesDAO.find_one_or_none(name=key)
    if property_value:
        # await redis_client.set(key, PropertySchema.from_orm(property_value).model_dump_json(), ex=3600)
        return property_value
    raise HTTPException(status_code=404, detail="Property not found")


@router.post("/property")
async def create_property(property_data: PropertyCreationSchema) -> PropertySchema:
    """
    Create a new property.
    """
    property_value = await PropertiesDAO.add(**property_data.dict())
    if property_value:
        return property_value
    raise HTTPException(status_code=400, detail="Property not created")


@router.delete("/property/{key}")
async def delete_property(key: str) -> PropertySchema:
    """
    Delete a property by key.
    """
    property = await PropertiesDAO.find_one_or_none(name=key)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    deleted = await PropertiesDAO.delete(model_id=property.id)
    if not deleted:
        return property
    raise HTTPException(status_code=404, detail="Property not found")


@router.put("/property/{key}")
async def update_property(key: str, value: str) -> PropertySchema:
    """
    Update a property by key.
    """
    property = await PropertiesDAO.find_one_or_none(name=key)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    updated_property = await PropertiesDAO.update(model_id=property.id, name=key, value=value)
    if updated_property:
        await redis_client.set("season_id", value=value)
        return updated_property
    raise HTTPException(status_code=404, detail="Property not found")


@router.get("/users")
async def get_all_users() -> list[UserSchema]:
    """
    Get all users.
    """
    users = await UsersDAO.find_all()
    if users:
        return users
    raise HTTPException(status_code=404, detail="No users found")


@router.get("/group/{chat_id}")
@redis_cache(schema=GroupSchema, key_func=lambda chat_id: f"group:{chat_id}", expire=1200)
async def get_group(chat_id: str) -> GroupSchema:
    """
    Get group by chat_id.
    """
    group = await GroupsDAO.find_one_or_none(chat_id=chat_id)
    if group:
        return group
    raise HTTPException(status_code=404, detail="Group not found")


@router.post("/group")
async def create_group(group_data: GroupCreationSchema) -> GroupSchema:
    """
    Create a new group.
    """
    group = await GroupsDAO.add(**group_data.dict())
    if group:
        return group
    raise HTTPException(status_code=400, detail="Group not created")


@router.get("/groups")
async def get_all_groups() -> list[GroupSchema]:
    """
    Get all groups.
    """
    groups = await GroupsDAO.find_all()
    if groups:
        return groups
    raise HTTPException(status_code=404, detail="No groups found")
