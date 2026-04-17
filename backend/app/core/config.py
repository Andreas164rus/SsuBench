from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'База'
    DATABASE_URL: str
    secret: str = 'SECRET' # this's for user's password
    first_name_admin: str
    last_name_admin: str

    class Config:
        env_file = '.env'


settings = Settings()
