from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app settings. Values come from environment variables / the .env file."""

    app_name: str = "MealConnect API"
    app_subtitle: str = "Food Sharing & Reservation System"
    app_version: str = "0.3.0"
    app_env: str = "development"  # development | production
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # No default on purpose: the app must refuse to start without a database URL.
    database_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()