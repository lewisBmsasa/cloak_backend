from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    app_name: str = "PII Detector"
    debug: bool = True

    # Paths to prompt files
    detect_prompt_path: str = "prompts/detect.txt"
    abstract_prompt_path: str = "prompts/abstract.txt"

    # Loaded prompts (lazy-loaded from files)
    @property
    def system_prompts(self):
        return {
            "detect": Path(self.detect_prompt_path).read_text(),
            "abstract": Path(self.abstract_prompt_path).read_text(),
        }

    class Config:
        env_file = ".env"

settings = Settings()
