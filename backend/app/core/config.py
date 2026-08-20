from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment / .env."""

    app_name: str = "food-logger"
    app_env: str = "development"
    debug: bool = True

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "foodlogger"
    mysql_password: str = "foodlogger"
    mysql_database: str = "food_logger"
    database_url: str = (
        "mysql+pymysql://foodlogger:foodlogger@localhost:3306/food_logger"
    )

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
