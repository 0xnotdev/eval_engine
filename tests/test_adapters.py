import pytest
from eval_engine.adapters import get_adapter

def test_get_adapter_allowlist_kwargs():
    # Provide unexpected kwargs alongside expected ones
    kwargs = {
        "api_key": "test_key",
        "unexpected_kwarg": "should_be_ignored",
        "api_base": "http://localhost:8000"
    }
    
    # Just need to make sure get_adapter doesn't crash from unexpected kwargs
    try:
        adapter = get_adapter("openai_compatible", target_endpoint="http://localhost/v1/chat/completions", **kwargs)
        # Assuming the adapter successfully instantiates
        assert adapter is not None
    except TypeError as e:
        pytest.fail(f"get_adapter failed with TypeError: {e}")
