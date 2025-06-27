from sqlalchemy import select, insert, update, delete

from app.dao.base import BaseDAO
from app.bot.models import Properties, Users, Groups, Feedbacks


class PropertiesDAO(BaseDAO):
    model = Properties


class UsersDAO(BaseDAO):
    model = Users

    
class GroupsDAO(BaseDAO):
    model = Groups


class FeedbacksDAO(BaseDAO):
    model = Feedbacks