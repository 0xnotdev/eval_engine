from typing import Dict, Any, Optional
from pydantic import BaseModel

class ScoreResult(BaseModel):
    score: float
    passed: bool
    reasoning: Optional[str] = None

class BaseScorer:
    """Abstract interface for all scorers."""
    
    async def score(self, expected: Any, actual: str, **kwargs) -> ScoreResult:
        """Calculate score. 
        `expected` could be a golden string, regex pattern, or JSON object depending on the scorer.
        `actual` is the response text from the target model.
        """
        raise NotImplementedError("Scorers must implement score()")
