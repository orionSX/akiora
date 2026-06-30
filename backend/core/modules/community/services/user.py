from community.models import User


class UserService:
    async def get_by_email(self, email: str):
        return await User.find_one(User.email == email)

    async def login(self, email: str) -> User:
        u = await User.find_one(User.email == email)
        if u:
            return u
        new_user = User(email=email)
        await new_user.save()
        return new_user
