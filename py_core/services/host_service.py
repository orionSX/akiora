from models.host import Host
from utils.helpers import time_now
from uuid import UUID
from models.enums import HostStatus
from typing import Optional


class HostService:
    async def get_by_id(self, id: str | UUID):
        return await Host.get(id)

    async def get_by_owner(self, id: str | UUID):
        if type(id) is UUID:
            return await Host.find_one(Host.owner_id == id)
        elif type(id) is str:
            return await Host.find_one(Host.owner_id == UUID(id))
        return None

    async def create(self, owner_id: str):

        host = Host(owner_id=UUID(owner_id))
        await host.save()
        return host

    async def get_active_by_uid(self, user_id: str) -> Optional[Host]:
        return await Host.find_one(
            Host.owner_id == UUID(user_id), Host.status == HostStatus.ACTIVE
        )

    async def update(self, actor_id: UUID, id: str, patch: dict):
        host = await Host.get(id)
        if not host:
            raise
        if actor_id != host.owner_id:
            raise

        if patch.get("avatar_url") is not None:
            host.avatar_url = patch.get("avatar_url")
        if patch.get("about") is not None:
            host.about = patch.get("about")
        if patch.get("status") is not None:
            host.status = HostStatus(patch.get("status"))
        if val := patch.get("admins") is not None:
            add = val.get("append")
            rmv = val.get("remove")
            host.admins = [x for x in host.admins if str(x) not in rmv]
            for x in add:
                host.admins.append(UUID(x))

        host.updated_at = time_now()
        await host.save()
        return host

    async def update_admin(self, id: str | UUID, patch: dict):
        host = await Host.get(id)
        if not host:
            return None

        if patch.get("owner_id") is not None:
            host.owner_id = UUID(patch.get("owner_id"))
        if patch.get("avatar_url") is not None:
            host.avatar_url = patch.get("avatar_url")
        if patch.get("about") is not None:
            host.about = patch.get("about")
        if patch.get("status") is not None:
            host.status = HostStatus(patch.get("status"))

        host.updated_at = time_now()
        await host.save()
        return host
