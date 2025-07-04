from typing import Optional
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


class UserCreationSchema(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50, description="The username of the user")
    chat_id: str = Field(..., min_length=8, max_length=128, description="The chat ID of the user")

class UserSchema(BaseSchema):
    id: int
    username: str
    chat_id: str
    full_name: str | None = None
    description: str | None = None
    disabled: bool = False
    admin_level: int = 0
    is_banned: bool = False


class UserUpdateSchema(BaseSchema):
    username: Optional[str]
    chat_id: Optional[str]
    full_name: Optional[str]
    description: Optional[str]
    disabled: Optional[bool]
    admin_level: Optional[int]
    is_banned: Optional[bool]


class FeedbackCreationSchema(BaseSchema):
    chat_id: str
    message: str = Field(..., min_length=1, max_length=500, description="Feedback message from the user")
    is_fixed: bool = False


class FeedbackSchema(BaseSchema):
    id: int
    user_id: int | None
    chat_id: str
    message: str
    is_fixed: bool = False


class PropertySchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100, description="The name of the property")
    value: str = Field(..., min_length=1, max_length=500, description="The value of the property")
    description: str | None = Field(None, max_length=500, description="Description of the property")


class PropertyCreationSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100, description="The name of the property")
    value: str = Field(..., min_length=1, max_length=500, description="The value of the property")
    description: str | None = Field(None, max_length=500, description="Description of the property")


class GroupSchema(BaseSchema):
    id: int
    name: str
    chat_id: str
    description: str | None = None
    disabled: bool = False


class GroupCreationSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100, description="The name of the group")
    chat_id: str = Field(..., min_length=8, max_length=128, description="The chat ID of the group")
    disabled: bool = False
