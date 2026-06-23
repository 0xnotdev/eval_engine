import yaml
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class AdapterConfig(BaseModel):
    type: str = Field(default="openai_compatible")
    headers: Dict[str, str] = Field(default_factory=dict)
    kwargs: Dict[str, Any] = Field(default_factory=dict)

class Config(BaseModel):
    target: AdapterConfig = Field(default_factory=AdapterConfig)
    judge: Optional[AdapterConfig] = None
    dataset_path: Optional[str] = None
    stress: Dict[str, Any] = Field(default_factory=lambda: {"concurrency": 10, "max_parallel": 10})

class ConfigLoader:
    @staticmethod
    def load(config_path: str) -> Config:
        if not os.path.exists(config_path):
            # Return defaults
            return Config()
            
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            
        return Config(**data)
