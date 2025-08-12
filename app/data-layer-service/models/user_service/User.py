from models.Document import Document
from pydantic import BaseModel, EmailStr, Field
from schemas.user_service.User import GetUser, CreateUser
from schemas.user_service.user_complex_fields import Socials
from typing import List, Dict, Any

from datetime import datetime, UTC
from bson import ObjectId


def default_league_roles():
    return ["TOP", "JG", "MID", "ADC", "SUP"]


def utc_now():
    return datetime.now(UTC)


def default_roles():
    return ["user"]


def default_socials():
    return Socials()


class User(Document):
    nickname: str = Field(..., min_length=1, max_length=100)
    gender: str = Field(default="", description="male | female | ...", max_length=750)
    # roles:List[str]=Field(default_factory=default_roles,description='user | admin etc roles')
    league_roles: List[str] = Field(
        default_factory=default_league_roles,
        min_length=1,
        max_length=5,
        description="Roles prio descending ['TOP', 'JG', 'MID', 'ADC', 'SUP'] ",
    )
    # email: EmailStr = Field(...)
    riot_accounts: List[str] = Field(
        default_factory=list, description="array of links to opgg | smth else maybe"
    )
    created_at: datetime = Field(default_factory=utc_now)
    socials: Socials = Field(default_factory=default_socials)

    @classmethod
    async def get_find_query(cls, data: BaseModel) -> Dict[str, Any]:
        query = dict()
        if isinstance(data, GetUser):
            conditions = []

            if data.ids:
                if len(data.ids) == 1:
                    conditions.append({"_id": ObjectId(data.ids[0])})
                else:
                    conditions.append({"_id": {"$in": [ObjectId(x) for x in data.ids]}})

            if data.nicknames:
                if len(data.nicknames) == 1:
                    conditions.append({"nickname": data.nicknames[0]})
                else:
                    conditions.append({"nickname": {"$in": data.nicknames}})

            if conditions:
                if data.conjuction:
                    query["$and"] = conditions
                else:
                    query["$or"] = conditions

        return query

    @classmethod
    async def get_update_data(cls, data: BaseModel) -> Dict[str, Any]: ...

    @classmethod
    async def get_create_data(cls, data: BaseModel) -> List[Dict[str, Any]]:
        if isinstance(data, CreateUser):
            return [data.model_dump(exclude={"id"})]
        return []
