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

    mongo_url: str = "mongodb://localhost:27017/?replicaSet=rs0"
    mongo_db: str = "game_service_db"

    env_type: str = "IGNORE"
    secret_key: str = "123"
    grpc_port: int = 50051


settings = Settings()
