from .base import BaseScorer, ScoreResult
from typing import Any

class LatencySloScorer(BaseScorer):
    """Scores based on whether the measured latency is under the SLO threshold."""
    
    async def score(self, expected: Any, actual: str, **kwargs) -> ScoreResult:
        # expected is the SLO threshold in ms
        try:
            threshold_ms = float(expected)
        except ValueError:
            return ScoreResult(score=0.0, passed=False, reasoning="Invalid latency threshold provided.")
            
        latency_ms = kwargs.get("latency_ms")
        if latency_ms is None:
            return ScoreResult(score=0.0, passed=False, reasoning="Latency metric missing from response.")
            
        passed = latency_ms <= threshold_ms
        
        # Calculate a continuous score (0 to 1) based on how far under/over the SLO we are.
        # e.g., exactly at threshold = 0.5. Half the threshold = 1.0. Double the threshold = 0.0
        if latency_ms == 0:
            score = 1.0
        else:
            score = max(0.0, min(1.0, 1.0 - ((latency_ms - threshold_ms) / threshold_ms) * 0.5))
            
        return ScoreResult(
            score=score if passed else 0.0,
            passed=passed,
            reasoning=f"Latency {latency_ms:.2f}ms vs SLO {threshold_ms:.2f}ms."
        )
