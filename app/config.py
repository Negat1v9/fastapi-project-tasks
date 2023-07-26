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
    REDIS_URL: str
    # sender email env value
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    
    class Config:
        env_file = ".env-non-dev"
        
settings: Settings = Settings()