from .base import BaseAdapter, AdapterResponse
from .openai_compatible import OpenAICompatibleAdapter
from .anthropic import AnthropicAdapter
from .generic_http import GenericHttpAdapter

def get_adapter(adapter_type: str, target_endpoint: str, headers: dict = None, **kwargs) -> BaseAdapter:
    if adapter_type == "openai_compatible":
        return OpenAICompatibleAdapter(target_endpoint, headers, **kwargs)
    elif adapter_type == "anthropic":
        return AnthropicAdapter(target_endpoint, headers, **kwargs)
    elif adapter_type == "generic_http":
        return GenericHttpAdapter(target_endpoint, headers, **kwargs)
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")
