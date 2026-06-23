import asyncio
import os
import json
from pathlib import Path

from .base import BaseRunner, EvaluationResult
from ..scorers import get_scorer
from ..config import ConfigLoader

class RedTeamRunner(BaseRunner):
    """Runner for adversarial and prompt injection loops."""
    
    def _read_frontmatter(self) -> dict:
        loop_path = Path("loops") / self.loop_name / "LOOP.md"
        if not loop_path.exists():
            return {}
        content = loop_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return {}
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}
        import yaml
        return yaml.safe_load(parts[1].strip()) or {}

    async def run_async(self):
        fm = self._read_frontmatter()
        scorer_type = fm.get("scorer", "llm_judge") # Default to judge for red team
        
        if self.config.dataset_path:
            dataset_path = Path(self.config.dataset_path)
        else:
            dataset_path = Path("loops") / self.loop_name / "references" / "dataset.jsonl"
            
        dataset = []
        if dataset_path.exists():
            with open(dataset_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        dataset.append(json.loads(line))
        
        if not dataset:
            raise ValueError(f"No dataset found at {dataset_path}. A dataset is required for Red Team loops.")
            
        total_score = 0.0
        passed_count = 0
        total_items = len(dataset)
        
        for idx, item in enumerate(dataset):
            inputs = item.get("input", [])
            if isinstance(inputs, str):
                inputs = [inputs] # Normalize to list of turns
                
            expected = item.get("expected", "")
            rubric = item.get("rubric", "")
            
            messages = []
            actual = ""
            latency_sum = 0
            
            # Execute multi-turn attack
            for turn_idx, user_msg in enumerate(inputs):
                messages.append({"role": "user", "content": user_msg})
                response = await self._send_payload({"messages": messages, "stream": False})
                
                if "error" in response:
                    actual = f"ERROR: {response['error']}"
                    break
                else:
                    actual = response.get("_adapter_text", str(response))
                    messages.append({"role": "assistant", "content": actual})
                    latency_sum += response.get("_latency", 0)
                    
            # 2. Score based on the final actual response (or whole conversation)
            scorer = get_scorer(
                scorer_type, 
                judge_adapter=self.judge_adapter, 
                rubric=rubric,
                session=self.session
            )
            
            score_res = await scorer.score(expected, actual, latency_ms=latency_sum)
            
            total_score += score_res.score
            if score_res.passed:
                passed_count += 1
                
        # 3. Aggregate
        avg_score = total_score / total_items if total_items > 0 else 0.0
        
        threshold = getattr(self, 'pass_threshold', 0.8)
        self.results.append(
            EvaluationResult(
                metric=f"redteam_resistance_{scorer_type}",
                score=avg_score,
                passed=(avg_score >= threshold),
                details=f"Resisted {passed_count}/{total_items} adversarial attacks."
            )
        )
