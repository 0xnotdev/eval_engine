from .base import BaseScorer, ScoreResult
from typing import Any
import math
import litellm

class EmbeddingSimilarityScorer(BaseScorer):
    """Scores based on cosine similarity between actual and expected text embeddings."""
    
    def __init__(self, model: str = "text-embedding-3-small", threshold: float = 0.85, **kwargs):
        # kwargs (e.g. `session`) is accepted and ignored; runners pass it uniformly.
        self.model = model
        self.threshold = threshold
        
    def cosine_similarity(self, v1, v2):
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(a * a for a in v1))
        magnitude2 = math.sqrt(sum(b * b for b in v2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    async def score(self, expected: Any, actual: str, **kwargs) -> ScoreResult:
        expected_str = str(expected)
        
        try:
            # We fetch embeddings in parallel
            import asyncio
            responses = await asyncio.gather(
                litellm.aembedding(model=self.model, input=[expected_str]),
                litellm.aembedding(model=self.model, input=[actual])
            )
            
            emb_expected = responses[0].data[0]['embedding']
            emb_actual = responses[1].data[0]['embedding']
            
            similarity = self.cosine_similarity(emb_expected, emb_actual)
            passed = similarity >= self.threshold
            
            return ScoreResult(
                score=similarity,
                passed=passed,
                reasoning=f"Cosine similarity: {similarity:.3f} (Threshold: {self.threshold})"
            )
            
        except Exception as e:
            return ScoreResult(
                score=0.0,
                passed=False,
                reasoning=f"Embedding generation failed: {str(e)}"
            )
