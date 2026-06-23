import aiohttp
import time
from typing import List, Dict, Any
from .base import BaseAdapter, AdapterResponse

class OpenAICompatibleAdapter(BaseAdapter):
    """Adapter for endpoints that accept /chat/completions schema (OpenAI, vLLM, Ollama)."""
    
    async def send(self, session: aiohttp.ClientSession, messages: List[Dict[str, str]], **kwargs) -> AdapterResponse:
        payload = {
            "messages": messages,
            "stream": False
        }
        # Allow overriding model, temperature, etc via config kwargs or runtime kwargs
        payload.update(self.kwargs)
        payload.update(kwargs)
        
        # Ensure a default model is provided if missing
        if "model" not in payload:
            payload["model"] = "gpt-3.5-turbo"
            
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
                
                # Extract text
                text = ""
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        text = choice["message"]["content"]
                        
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
