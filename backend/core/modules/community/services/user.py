from modules.community.models import User
from modules.utils import time_now
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

    async def update_user(self, id: str | UUID, patch: dict):
        user = await User.get(id)
        if not user:
            return None

        for field in ("email", "avatar_url", "about", "nickname", "league_accounts"):
            if field in patch:
                setattr(user, field, patch[field])

        user.updated_at = time_now()
        await user.save()
        return user
