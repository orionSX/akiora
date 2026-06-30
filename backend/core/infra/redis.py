from typing import Any, TypeVar, overload

import msgspec
from pydantic import BaseModel
from redis.asyncio import Redis

T = TypeVar("T", bound=BaseModel)


class RedisService:
    def __init__(
        self,
        redis_client: Redis,
        ttl: int = 0,
    ):
        self.redis = redis_client
        self.ttl = ttl if ttl != 0 else 30 * 60

    async def create(
        self,
        key: str,
        value: dict,
        ttl: int = 0,
    ):
        if ttl == 0:
            ttl = self.ttl

        data = msgspec.json.encode(value)

        await self.redis.setex(key, ttl, data)

    @overload
    async def get(self, key: str, obj_type: type[T]) -> T: ...

    @overload
    async def get(self, key: str, obj_type: None = None) -> dict: ...

    async def get(
        self,
        key: str,
        obj_type: type[T] | None = None,
    ) -> T | dict:
        data_raw = await self.redis.get(key)
        if not data_raw:
            raise Exception("Value doesnt exist for this key")
        data = msgspec.json.decode(data_raw)
        if not obj_type:
            return data

        return obj_type(**data)

    async def delete(self, pattern: str):
        await self.redis.delete(pattern)

    async def publish_pubsub(self, channel: str, message: dict):
        await self.redis.publish(channel, msgspec.json.encode(message))

    async def publish_stream(self, stream: str, message: dict[str, Any]):
        await self.redis.xadd(stream, {"payload": msgspec.json.encode(message)})

    async def read_stream(
        self,
        stream: str,
        last_id: str = "$",
        block_ms: int = 30000,
        count: int = 50,
    ) -> list[tuple[str, dict[str, Any]]]:
        entries = await self.redis.xread({stream: last_id}, block=block_ms, count=count)
        messages: list[tuple[str, dict[str, Any]]] = []
        for _, stream_messages in entries:
            for message_id, fields in stream_messages:
                payload = fields.get("payload")
                if payload is None:
                    continue
                if isinstance(payload, str):
                    payload = payload.encode()
                messages.append((message_id, msgspec.json.decode(payload)))
        return messages
