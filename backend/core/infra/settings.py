from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
        env_file=".env",
    )

    redis_url: str = "redis://localhost:6379/0"
    redis_ttl: int = 0

    env_type: str = "IGNORE"

    secret_key: str = "secret"

    smtp_server: str = "smtp.example.com"
    smtp_port: int = 587
    email_address: str = "noreply@example.com"
    email_password: str = ""

    yandex_cid: str = ""
    yandex_cs: str = ""
    discord_cid: str = ""
    discord_cs: str = ""

    community_grpc_address: str = "localhost:50051"

    # Comma-separated list of extra CORS origins. Lets ops add new server IPs
    # without code edits — e.g. ALLOWED_ORIGINS="http://1.2.3.4:3000,..."
    allowed_origins: str = ""


settings = Settings()
