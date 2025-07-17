from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017/youruniverse"
    JWT_SECRET_KEY: str = "supersecretkey"
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = "amarjeet.boffinblocks@gmail.com"
    EMAIL_PASSWORD: str = "your_app_password"
    EMAIL_FROM: str = "amarjeet.boffinblocks@gmail.com"
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
