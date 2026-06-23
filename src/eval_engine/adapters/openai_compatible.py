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
                if response.status >= 400:
                    text = await response.text()
                    end_t = time.time()
                    return AdapterResponse(
                        text="",
                        raw={"error": text},
                        latency_ms=(end_t - start_t) * 1000,
                        status_code=response.status,
                        error=f"HTTP {response.status}: {text}"
                    )
                
                if payload.get("stream"):
                    text = ""
                    ttft_ms = None
                    async for line in response.content:
                        if line:
                            if ttft_ms is None:
                                ttft_ms = (time.time() - start_t) * 1000
                            # Extract basic SSE payload without full json parsing for speed if needed
                            # but we need to extract text to count tokens/length if no usage info
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith("data: ") and line_str != "data: [DONE]":
                                import json
                                try:
                                    chunk = json.loads(line_str[6:])
                                    if "choices" in chunk and len(chunk["choices"]) > 0:
                                        delta = chunk["choices"][0].get("delta", {})
                                        text += delta.get("content", "")
                                except:
                                    pass
                    end_t = time.time()
                    return AdapterResponse(
                        text=text,
                        raw={"streamed": True},
                        latency_ms=(end_t - start_t) * 1000,
                        ttft_ms=ttft_ms,
                        status_code=response.status
                    )
                else:
                    data = await response.json()
                    end_t = time.time()
                    latency_ms = (end_t - start_t) * 1000
                    
                    text = ""
                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            text = choice["message"]["content"]
                            
                    return AdapterResponse(
                        text=text or "",
                        raw=data,
                        latency_ms=latency_ms,
                        ttft_ms=latency_ms, # if not streaming, ttft is total latency
                        status_code=response.status
                    )
        except Exception as e:
            return AdapterResponse(
                text="",
                raw={},
                status_code=0,
                error=str(e)
            )
