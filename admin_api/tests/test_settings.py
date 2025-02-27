from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class TestSettings(BaseSettings):
    PROJECT_NAME: str = "Library Management - ADMIN API Test"
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"
    POSTGRES_DB: str = "test_db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # RabbitMQ settings
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return self.DATABASE_URL
    
    model_config = ConfigDict(
        case_sensitive=True
    )

test_settings = TestSettings()