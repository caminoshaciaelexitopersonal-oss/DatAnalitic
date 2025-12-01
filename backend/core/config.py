import os

class AppConfig:
    PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "data/processed")

config = AppConfig()
