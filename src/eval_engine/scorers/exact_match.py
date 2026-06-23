from .base import BaseScorer, ScoreResult
from typing import Any

class ExactMatchScorer(BaseScorer):
    """Scores 1.0 if actual matches expected exactly (case-insensitive option)."""
    
    def __init__(self, case_sensitive: bool = False, strip: bool = True):
        self.case_sensitive = case_sensitive
        self.strip = strip
        
    async def score(self, expected: Any, actual: str, **kwargs) -> ScoreResult:
        expected_str = str(expected)
        
        if self.strip:
            expected_str = expected_str.strip()
            actual = actual.strip()
            
        if not self.case_sensitive:
            expected_str = expected_str.lower()
            actual = actual.lower()
            
        passed = (expected_str == actual)
        
        return ScoreResult(
            score=1.0 if passed else 0.0,
            passed=passed,
            reasoning=f"Expected '{expected_str}', got '{actual}'"
        )
