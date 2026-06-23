import asyncio
import os
import json
from pathlib import Path

from .base import BaseRunner, EvaluationResult
from ..scorers import get_scorer
from ..config import ConfigLoader

class EvaluationRunner(BaseRunner):
    """Runner for standard metric-based LLM evaluations."""
    
    def _read_frontmatter(self) -> dict:
        # Assumes working directory is the loop dir (as agent.py is inside it, or we find it)
        # However, runner is initialized with `loop_name`. The path is loops/<loop_name>/LOOP.md
        loop_path = Path("loops") / self.loop_name / "LOOP.md"
        if not loop_path.exists():
            return {}
            
        content = loop_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return {}
            
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}
            
        yaml_text = parts[1].strip()
        import yaml
        return yaml.safe_load(yaml_text) or {}

    async def run_async(self):
        fm = self._read_frontmatter()
        scorer_type = fm.get("scorer", "exact_match")
        
        # Load dataset
        dataset_path = Path("loops") / self.loop_name / "references" / "dataset.jsonl"
        dataset = []
        if dataset_path.exists():
            with open(dataset_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        dataset.append(json.loads(line))
        else:
            # Fallback for loops without dataset yet (e.g. while building)
            dataset = [{"input": "Hello", "expected": "Hello"}]
            
        total_score = 0.0
        passed_count = 0
        total_items = len(dataset)
        
        for idx, item in enumerate(dataset):
            prompt = item.get("input", "")
            expected = item.get("expected", "")
            rubric = item.get("rubric", "")
            
            # 1. Send to target
            response = await self._send_payload({"messages": [{"role": "user", "content": prompt}], "stream": False})
            
            if "error" in response:
                actual = f"ERROR: {response['error']}"
            else:
                actual = response.get("_adapter_text", str(response))
                
            # 2. Score
            scorer = get_scorer(
                scorer_type, 
                judge_adapter=self.judge_adapter, 
                rubric=rubric,
                session=self.session
            )
            
            score_res = await scorer.score(expected, actual, latency_ms=response.get("_latency"))
            
            total_score += score_res.score
            if score_res.passed:
                passed_count += 1
                
        # 3. Aggregate
        avg_score = total_score / total_items if total_items > 0 else 0.0
        
        self.results.append(
            EvaluationResult(
                metric=f"aggregate_{scorer_type}",
                score=avg_score,
                passed=(avg_score >= 0.8), # Arbitrary threshold for overall loop
                details=f"Passed {passed_count}/{total_items} evaluation items."
            )
        )
