import json
from pathlib import Path

CONFIG_FILE = Path("config.json")


class Config:
    def __init__(self):
        self.empresa = "Empresa Demo"
        self.responsable = "Administrador"
        self.stock_minimo = 5

    def load(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.__dict__.update(data)

    def save(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, indent=4, ensure_ascii=False)


config = Config()
config.load()
