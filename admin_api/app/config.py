import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, computed_field

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file = "admin_api/.env",
        env_file_encoding = "utf-8",
        case_sensitive = True
    )

    PROJECT_NAME: str = "Library Management - ADMIN API"
    
    # Database settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int 
    DATABASE_URL: str
    
    # RabbitMQ settings
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings()