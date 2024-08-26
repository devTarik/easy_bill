
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    openapi_url: str = "/openapi.json"

    db_name: str = ""
    db_user: str = ""
    db_password: str = ""
    db_host: str = ""
    db_port: str = "5432"
    db_driver: str = "postgresql+asyncpg"

    jwt_secret_key: str = "2JxQpLZ4lR7D1fFzJ8cK5n9W2yH3sA0T"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    receipt_shop_name: str = "АТБ"
    receipt_row_length: int = 40

    unit_test: bool = False

    @property
    def source_database_url(self) -> str:
        return f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def test_database_url(self) -> str:
        return f"{self.source_database_url}_tests"

    @property
    def database_url(self) -> str:
        if self.unit_test is True:
            return self.test_database_url
        return self.source_database_url


settings = Settings()
