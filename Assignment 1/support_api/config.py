from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    # grabs data from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SUPPORT_API_", extra="ignore")


    # Default databath, assuming no .env file
    data_path: Path = Path("data/restock_manifest.json")
