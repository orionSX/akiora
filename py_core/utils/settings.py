from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
        env_file=".env",
    )

    core_host: str = "0.0.0.0"
    core_port: int = 8000

    redis_url: str = "redis://localhost:6379/0"
    redis_ttl: int = 300

    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "game_service_db"

    env_type: str = "local"
    secret_key: str = "change-me"
    grpc_port: int = 50051

    smtp_server: str = "localhost"
    smtp_port: int = 1025
    email_address: str = "noreply@example.com"
    email_password: str = ""


settings = Settings()
