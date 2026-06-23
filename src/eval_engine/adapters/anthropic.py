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
                
        # Handle response_format for structured JSON
        requires_json = False
        response_format = self.kwargs.get("response_format") or kwargs.get("response_format")
        if response_format and isinstance(response_format, dict):
            if response_format.get("type") == "json_object":
                requires_json = True
                
        if requires_json:
            system_prompt += "\n\n<json_format_enforced>\nYou MUST output valid JSON format and nothing else. Do not wrap in markdown blocks.\n</json_format_enforced>\n"
            
        payload = {
            "messages": filtered_messages,
        }
        if system_prompt:
            payload["system"] = system_prompt.strip()
            
        # Explicit Kwarg Allowlist for Anthropic
        # Anthropic supports: model, max_tokens, temperature, top_p, stream, tools, tool_choice, metadata, stop_sequences
        ALLOWLIST = {"model", "max_tokens", "temperature", "top_p", "stream", "tools", "tool_choice", "metadata", "stop_sequences"}
        
        merged_kwargs = {**self.kwargs, **kwargs}
        for k, v in merged_kwargs.items():
            if k in ALLOWLIST:
                payload[k] = v
            else:
                import logging
                logging.debug(f"AnthropicAdapter: Dropping unsupported kwarg '{k}'")
                
        # Default model
        if "model" not in payload:
            payload["model"] = "claude-3-haiku-20240307"
            
        # Anthropic requires max_tokens
        if "max_tokens" not in payload:
            payload["max_tokens"] = 1024
            
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
