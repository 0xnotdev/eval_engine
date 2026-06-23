import aiohttp
import time
import json
from typing import List, Dict, Any, Optional
from .base import BaseAdapter, AdapterResponse

class GenericHttpAdapter(BaseAdapter):
    """Fallback adapter configurable via JSONPath for arbitrary APIs."""
    
    def _extract_jsonpath(self, data: Dict[str, Any], path: str) -> str:
        """Simple dot-path extractor (e.g., 'response.data.text')."""
        try:
            parts = path.split('.')
            curr = data
            for part in parts:
                if isinstance(curr, list) and part.isdigit():
                    curr = curr[int(part)]
                else:
                    curr = curr[part]
            return str(curr)
        except (KeyError, TypeError, IndexError):
            return ""

    async def send(self, session: aiohttp.ClientSession, messages: List[Dict[str, str]], **kwargs) -> AdapterResponse:
        # User needs to provide a payload_template in kwargs
        # e.g. payload_template = {"prompt": "{messages}", "max_length": 500}
        payload_template = self.kwargs.get("payload_template", {"messages": "{messages}"})
        response_jsonpath = self.kwargs.get("response_jsonpath", "text")
        
        # Super simple template replacement for now
        # A more robust system would use Jinja2
        payload_str = json.dumps(payload_template)
        payload_str = payload_str.replace('"{messages}"', json.dumps(messages))
        payload = json.loads(payload_str)
        
        start_t = time.time()
        try:
            async with session.post(self.target_endpoint, json=payload, headers=self.headers, timeout=30) as response:
                end_t = time.time()
                latency_ms = (end_t - start_t) * 1000
                
                if response.status >= 400:
                    text = await response.text()
                    return AdapterResponse(
                        text="",
                        raw={"error": text},
                        latency_ms=latency_ms,
                        status_code=response.status,
                        error=f"HTTP {response.status}: {text}"
                    )
                
                data = await response.json()
                text = self._extract_jsonpath(data, response_jsonpath)
                        
                return AdapterResponse(
                    text=text,
                    raw=data,
                    latency_ms=latency_ms,
                    status_code=response.status
                )
        except Exception as e:
            return AdapterResponse(
                text="",
                raw={},
                status_code=0,
                error=str(e)
            )
