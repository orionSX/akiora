from models.user import User
from utils.helpers import time_now
from uuid import UUID


class UserService:
    async def get_by_id(self, id: str | UUID):
        return await User.get(id)

    async def get_by_email(self, email: str):
        return await User.find_one(User.email == email)

    async def login(self, email: str) -> User:
        u = await User.find_one(User.email == email)
        if u:
            return u
        new_user = User(email=email)
        await new_user.save()
        return new_user

    async def update(self, id: str | UUID, patch: dict):
        user = await User.get(id)
        if not user:
            return None

        if patch.get("nickname") is not None:
            user.nickname = patch.get("nickname")
        if patch.get("avatar_url") is not None:
            user.avatar_url = patch.get("avatar_url")
        if patch.get("about") is not None:
            user.about = patch.get("about")

        user.updated_at = time_now()
        await user.save()
        return user
