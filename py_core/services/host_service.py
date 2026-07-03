from models.host import Host
from utils.helpers import time_now
from uuid import UUID


class HostService:
    async def get_by_id(self, id: str | UUID):
        return await Host.get(id)

    async def create(self, owner_id: str | UUID):
        host = Host(owner_id=owner_id)
        await host.save()
        return host

    async def update(self, id: str | UUID, patch: dict):
        host = await Host.get(id)
        if not host:
            return None

        if patch.get("nickname") is not None:
            host.nickname = patch.get("nickname")
        if patch.get("avatar_url") is not None:
            host.avatar_url = patch.get("avatar_url")
        if patch.get("about") is not None:
            host.about = patch.get("about")

        host.updated_at = time_now()
        await host.save()
        return host
