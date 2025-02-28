from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class TestEnvSettings(BaseSettings):
   model_config = ConfigDict(
       env_file = None,
       case_sensitive = True
   )

   PROJECT_NAME: str = "Library Management - FRONTEND API Test"
   
   # Database settings (using SQLite for tests)
   POSTGRES_SERVER: str = "localhost"
   POSTGRES_USER: str = "test_user"
   POSTGRES_PASSWORD: str = "test_password"
   POSTGRES_DB: str = "test_db"
   POSTGRES_PORT: int = 5432
   DATABASE_URL: str = "sqlite:///./test.db"
   
   # Mock RabbitMQ settings
   RABBITMQ_HOST: str = "localhost"
   RABBITMQ_PORT: int = 5672
   RABBITMQ_USER: str = "guest"
   RABBITMQ_PASSWORD: str = "guest"

test_settings = TestEnvSettings()