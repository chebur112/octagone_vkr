from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file= ".env", extra="ignore")
    
    bot_token: str
    admin_ids: str 
    yc_folder_id: str
    yc_api_key: str
    unf_base_url: str
    unf_user: str
    unf_password: str = ""
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "db"
    postgres_port:int = 5432
    

    @property
    def admin_id_list(self):
        return [int(x) for x in self.admin_ids.split(",") if x.strip()]
    
    
    @property
    def database_url(self):
        return (
        f"postgresql+asyncpg://" 
        f"{self.postgres_user}:"
        f"{self.postgres_password}@" 
        f"{self.postgres_host}:"
        f"{self.postgres_port}/"
        f"{self.postgres_db}"
    )
        
settings = Settings()
