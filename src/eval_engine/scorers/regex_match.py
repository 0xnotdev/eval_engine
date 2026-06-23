from .base import BaseScorer, ScoreResult
from typing import Any
import re

class RegexMatchScorer(BaseScorer):
    """Scores 1.0 if the actual response matches the expected regex pattern."""
    
    async def score(self, expected: Any, actual: str, **kwargs) -> ScoreResult:
        pattern = str(expected)
        try:
            match = re.search(pattern, actual)
            passed = bool(match)
            return ScoreResult(
                score=1.0 if passed else 0.0,
                passed=passed,
                reasoning=f"Regex '{pattern}' {'matched' if passed else 'did not match'} the response."
            )
        except re.error as e:
            return ScoreResult(
                score=0.0,
                passed=False,
                reasoning=f"Invalid regex pattern provided: {str(e)}"
            )
