from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import aiohttp

class AdapterResponse(BaseModel):
    """Normalized response from any adapter."""
    text: str
    raw: Dict[str, Any]
    latency_ms: Optional[float] = None
    ttft_ms: Optional[float] = None
    status_code: int
    error: Optional[str] = None

class BaseAdapter:
    """Abstract interface for target and judge adapters."""
    
    def __init__(self, target_endpoint: str, headers: Optional[Dict[str, str]] = None, **kwargs):
        self.target_endpoint = target_endpoint
        self.headers = headers or {}
        self.kwargs = kwargs
        
    async def send(self, session: aiohttp.ClientSession, messages: List[Dict[str, str]], **kwargs) -> AdapterResponse:
        """Send messages and return a normalized AdapterResponse."""
        raise NotImplementedError("Adapters must implement send()")
