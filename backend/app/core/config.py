from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app settings. Values come from environment variables / the .env file."""

    app_name: str = "MealConnect API"
    app_subtitle: str = "Food Sharing & Reservation System"
    app_version: str = "0.4.0"
    app_env: str = "development"  # development | production
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # No defaults on purpose: the app must refuse to start without these.
    database_url: str
    secret_key: str

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()