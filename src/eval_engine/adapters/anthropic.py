import aiohttp
import time
from typing import List, Dict, Any
from .base import BaseAdapter, AdapterResponse

class AnthropicAdapter(BaseAdapter):
    """Adapter for Anthropic's Messages API."""
    
    async def send(self, session: aiohttp.ClientSession, messages: List[Dict[str, str]], **kwargs) -> AdapterResponse:
        # Extract system prompt if present, as Anthropic expects it at top level
        system_prompt = ""
        filtered_messages = []
        for m in messages:
            if m.get("role") == "system":
                system_prompt += m.get("content", "") + "\\n"
            else:
                filtered_messages.append(m)
                
        payload = {
            "messages": filtered_messages,
        }
        if system_prompt:
            payload["system"] = system_prompt.strip()
            
        # Default model
        if "model" not in self.kwargs and "model" not in kwargs:
            payload["model"] = "claude-3-haiku-20240307"
            
        # Anthropic requires max_tokens
        if "max_tokens" not in self.kwargs and "max_tokens" not in kwargs:
            payload["max_tokens"] = 1024
            
        payload.update(self.kwargs)
        payload.update(kwargs)
        
        # Ensure anthropic-version header is set if missing
        headers = self.headers.copy()
        if "anthropic-version" not in {k.lower() for k in headers}:
            headers["anthropic-version"] = "2023-06-01"
            
        start_t = time.time()
        try:
            async with session.post(self.target_endpoint, json=payload, headers=headers, timeout=30) as response:
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
                
                # Extract text
                text = ""
                if "content" in data and len(data["content"]) > 0:
                    text = data["content"][0].get("text", "")
                        
                return AdapterResponse(
                    text=text or "",
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
