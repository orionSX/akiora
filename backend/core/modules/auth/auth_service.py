from infra.redis import RedisService
from infra.mail import MailSender
from modules.community.services import UserService
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from typing import Optional, Dict, Any, Tuple
from uuid import uuid7
from modules.utils import time_now
from datetime import timedelta
import secrets
import string


class AuthService:
    def __init__(
        self,
        secret_key: str,
        mailer: MailSender,
        redis_service: RedisService,
        user_service: UserService,
    ):
        self.mailer = mailer
        self.user_service = user_service
        self.secret_key = secret_key
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.rs = redis_service
        self.redis_prefix = "auth:secret:"
        self.email_verification_prefix = "auth:verify:"

    async def request_verification(self, email: str) -> Tuple[str, bool]:

        user = await self.user_service.login(email)

        verification_code = "".join(secrets.choice(string.digits) for _ in range(6))

        await self.rs.create(
            key=f"{self.email_verification_prefix}{email}",
            value={
                "code": verification_code,
                "user_id": str(user.id),
                "email": email,
            },
            ttl=300,
        )

        self.mailer.send_email(email, "auth", verification_code)

        token = self.serializer.dumps(
            {"email": email, "purpose": "email_verification"}, salt="email-verification"
        )

        return token

    async def verify_code_and_create_session(
        self, token: str, code: str
    ) -> Optional[Dict[str, Any]]:

        try:
            data = self.serializer.loads(
                token,
                salt="email-verification",
                max_age=300,
            )
            email = data.get("email")
            if not email:
                return None
        except (SignatureExpired, BadSignature):
            return None

        stored_data = await self.rs.get(
            key=f"{self.email_verification_prefix}{email}", obj_type=None
        )

        if not stored_data:
            return None

        stored_code = stored_data.get("code")
        if stored_code != code:
            return None

        user_id = stored_data.get("user_id")
        if not user_id:
            return None

        await self.rs.delete(f"{self.email_verification_prefix}{email}")

        session_token = await self._create_session(user_id, email)

        return {
            "user_id": user_id,
            "email": email,
            "session_token": session_token,
        }

    async def _create_session(self, user_id: str, email: str) -> str:

        session_id = str(uuid7())

        session_data = {
            "user_id": user_id,
            "email": email,
            "created_at": str(time_now()),
        }

        await self.rs.create(
            key=f"{self.redis_prefix}{session_id}",
            value=session_data,
            ttl=30 * 24 * 60 * 60,  # 30 дней
        )

        token = self.serializer.dumps(
            {"session_id": session_id, "user_id": user_id}, salt="session-auth"
        )

        return token

    async def verify_cookie_token(self, token: str) -> Optional[Dict[str, Any]]:

        try:
            data = self.serializer.loads(
                token, salt="session-auth", max_age=timedelta(days=30)
            )

            session_id = data.get("session_id")
            if not session_id:
                return None

            session_data = await self.rs.get(
                key=f"{self.redis_prefix}{session_id}", obj_type=None
            )

            if not session_data:
                return None

            return session_data

        except (SignatureExpired, BadSignature):
            return None

    async def refresh_session(self, token: str) -> Optional[str]:

        try:
            data = self.serializer.loads(token, salt="session-auth")
            session_id = data.get("session_id")
            user_id = data.get("user_id")

            if not session_id or not user_id:
                return None

            session_data = await self.rs.get(
                key=f"{self.redis_prefix}{session_id}", obj_type=None
            )

            if not session_data:
                return None

            await self.rs.create(
                key=f"{self.redis_prefix}{session_id}",
                value=session_data,
                ttl=30 * 24 * 60 * 60,
            )

            return self.serializer.dumps(
                {"session_id": session_id, "user_id": user_id}, salt="session-auth"
            )

        except (SignatureExpired, BadSignature):
            return None

    async def invalidate_session(self, token: str) -> bool:

        try:
            data = self.serializer.loads(token, salt="session-auth")
            session_id = data.get("session_id")
            if session_id:
                await self.rs.delete(f"{self.redis_prefix}{session_id}")
                return True
        except (SignatureExpired, BadSignature):
            pass
        return False
