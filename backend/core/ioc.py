from typing import AsyncIterator

from dishka import Provider, Scope, provide, make_async_container
from redis.asyncio import Redis


from modules.auth import AuthService
from modules.community.services import UserService
from modules.game import TournamentService
from infra import RedisManager, RedisService, MailSender, settings


class InfraProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    def get_mail_service(self) -> MailSender:
        return MailSender(
            settings.smtp_server,
            settings.smtp_port,
            settings.email_address,
            settings.email_password,
        )

    @provide(scope=Scope.APP)
    def get_redis_manager(self) -> RedisManager:
        return RedisManager(settings.redis_url)

    @provide(scope=Scope.REQUEST)
    async def get_redis_client(self, rm: RedisManager) -> AsyncIterator[Redis]:
        async with rm.get_client_context() as client:
            yield client

    @provide(scope=Scope.REQUEST)
    def get_redis_service(self, redis_client: Redis) -> RedisService:
        return RedisService(redis_client)


class ServiceProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.REQUEST)
    def get_user_service(self) -> UserService:
        return UserService()

    @provide(scope=Scope.REQUEST)
    def get_tournament_service(self) -> TournamentService:
        return TournamentService()

    @provide(scope=Scope.REQUEST)
    def get_auth_service(
        self,
        mail_service: MailSender,
        redis_service: RedisService,
        user_service: UserService,
    ) -> AuthService:
        return AuthService(
            secret_key=settings.secret_key,
            mailer=mail_service,
            redis_service=redis_service,
            user_service=user_service,
        )


container = make_async_container(InfraProvider(), ServiceProvider())
