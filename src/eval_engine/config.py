import yaml
import os
import re
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

# Matches ${VAR} and $VAR so secrets can be kept out of the config file.
_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")

def _expand_env(value: Any) -> Any:
    """Recursively expand ${VAR} references against the environment.

    This lets config.yaml reference secrets without embedding them, e.g.:
        Authorization: "Bearer ${OPENAI_API_KEY}"
    An unset variable expands to an empty string (so a missing key fails loudly
    at the API rather than leaking a literal '${...}' token).
    """
    if isinstance(value, str):
        return _ENV_PATTERN.sub(lambda m: os.environ.get(m.group(1), ""), value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value

class ConfigLoader:
    @staticmethod
    def load(config_path: str) -> Config:
        if not os.path.exists(config_path):
            # Return defaults
            return Config()

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # Resolve ${VAR} references (e.g. API keys) from the environment before
        # handing the config to the adapters, so secrets never live in the file.
        data = _expand_env(data)

        return Config(**data)
