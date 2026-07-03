import json
from typing import List, Any
from pydantic import AnyHttpUrl, BeforeValidator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

def parse_admin_ids(v: Any) -> List[int]:
    if isinstance(v, str):
        try:
            return [int(x.strip()) for x in json.loads(v)]
        except json.JSONDecodeError:
            return [int(x.strip()) for x in v.split(",") if x.strip()]
    if isinstance(v, list):
        return [int(x) for x in v]
    raise ValueError("Admin IDs must be a list or a JSON string list")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True, 
        extra="ignore"
    )

    PROJECT_NAME: str
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Telegram Bot
    BOT_TOKEN: str
    ADMIN_IDS: Annotated[List[int], BeforeValidator(parse_admin_ids)]
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, values: Any) -> Any:
        if isinstance(v, str) and v:
            return v
        
        # dynamic access to attributes from validation context
        data = values.data
        return (
            f"postgresql+asyncpg://{data.get('POSTGRES_USER')}:{data.get('POSTGRES_PASSWORD')}"
            f"@{data.get('POSTGRES_SERVER')}:{data.get('POSTGRES_PORT')}/{data.get('POSTGRES_DB')}"
        )

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    
    # Rate Limiting
    RATE_LIMIT_PERIOD: int = 1
    RATE_LIMIT_REQUESTS: int = 3

settings = Settings()

