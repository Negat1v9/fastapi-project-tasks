from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_MINUTS: int
    REFRESH_TOKEN_MINUTS: int
    REFRESH_SECRET: str
    
    class Config:
        env_file = ".env"
        
settings: Settings = Settings()