from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings_db(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER : str
    DB_PASS : str
    DB_NAME: str
    
    @property
    def DATABASE_URL_asyncpg(self):
        # postgresql+asyncpg://postgres:postgres@localhost:5432/sa
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file='.env',extra="ignore")
    
class Settings_bot(BaseSettings):
    TOKEN : str
    
    model_config = SettingsConfigDict(env_file='.env',extra="ignore")
    
class SettingsRedis(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    @property
    def REDIS_URL(self) -> str:
        return (f"redis://{self.REDIS_HOST}"
                f":{self.REDIS_PORT}/{self.REDIS_DB}")

    model_config = SettingsConfigDict(env_file='.env', extra="ignore")
    
class Admins_bot(BaseSettings):
    SUPER_ADMINS: List[int]
    model_config = SettingsConfigDict(env_file='.env',extra="ignore")
    

    
    
    
settings_db = Settings_db()
settings_bot = Settings_bot()
admins_bot = Admins_bot()
settings_redis = SettingsRedis()



        