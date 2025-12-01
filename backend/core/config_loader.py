import json
from pathlib import Path

class Config:
    _config = None

    @staticmethod
    def load():
        if Config._config is None:
            # Corrected path: .parents[1] navigates up from backend/core to backend/
            path = Path(__file__).resolve().parents[1] / "config/config.json"
            with open(path, "r") as f:
                Config._config = json.load(f)
        return Config._config
