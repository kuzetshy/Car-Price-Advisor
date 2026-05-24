import yaml
import os

class ConfigLoader:
    """Утилита для загрузки настроек из YAML файла."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"❌ Файл конфигурации не найден: {self.config_path}")
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, section: str) -> dict:
        """Получить определенную секцию конфига."""
        return self.config.get(section, {})