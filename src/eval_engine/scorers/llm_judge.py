from .base import BaseScorer, ScoreResult
from typing import Any, Optional
import json
import re

class LlmJudgeScorer(BaseScorer):
    """Uses a separate LLM adapter to evaluate the actual output against a rubric."""
    
    def __init__(self, judge_adapter, rubric: str):
        self.judge_adapter = judge_adapter
        self.rubric = rubric
        
    async def score(self, expected: Any, actual: str, **kwargs) -> ScoreResult:
        if not self.judge_adapter:
            return ScoreResult(score=0.0, passed=False, reasoning="No judge adapter configured.")
            
        system_prompt = (
            "You are an impartial AI judge evaluating a response. "
            "You must output ONLY valid JSON in the following schema: "
            '{"score": <float 0.0 to 1.0>, "reasoning": "<string justification>"}'
        )
        
        user_prompt = f"RUBRIC:\\n{self.rubric}\\n\\n"
        if expected:
            user_prompt += f"EXPECTED/CONTEXT:\\n{str(expected)}\\n\\n"
        user_prompt += f"ACTUAL RESPONSE:\\n{actual}\\n\\nEvaluate the actual response."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # We need the session from kwargs, or we create a new one just for this (not ideal, 
        # but the scorer interface doesn't pass session. I'll update it to accept session).
        session = kwargs.get("session")
        if not session:
            import aiohttp
            async with aiohttp.ClientSession() as s:
                response = await self.judge_adapter.send(s, messages, response_format={"type": "json_object"})
        else:
            response = await self.judge_adapter.send(session, messages, response_format={"type": "json_object"})
            
        if response.error:
            return ScoreResult(score=0.0, passed=False, reasoning=f"Judge error: {response.error}")
            
        text = response.text.strip()
        
        # Try to parse JSON
        try:
            # Often LLMs wrap JSON in markdown block
            match = re.search(r"```(?:json)?\\n(.*?)\\n```", text, re.DOTALL)
            if match:
                text = match.group(1)
                
            data = json.loads(text)
            score = float(data.get("score", 0.0))
            reasoning = data.get("reasoning", "No reasoning provided.")
            
            return ScoreResult(
                score=score,
                passed=(score >= 0.8), # Default threshold for judge passing
                reasoning=reasoning
            )
        except (json.JSONDecodeError, ValueError) as e:
            return ScoreResult(
                score=0.0,
                passed=False,
                reasoning=f"Judge returned invalid JSON: {text}. Error: {str(e)}"
            )
