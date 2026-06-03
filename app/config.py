class Settings:
    PROJECT_NAME: str = "SMEV Integration Gateway"
    
    ADAPTER_HOST: str = "localhost"
    ADAPTER_PORT: int = 7590
    ADAPTER_URL: str = f"http://{ADAPTER_HOST}:{ADAPTER_PORT}/ws"
    IS_MNEMONIC = "460A01"
    IN_DIR = "/opt/adapter/in"

settings = Settings()