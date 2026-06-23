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

    async def _evaluate_item(self, item: dict, scorer_type: str, semaphore: asyncio.Semaphore):
        """Evaluate a single dataset item, bounded by the concurrency semaphore."""
        async with semaphore:
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
            return score_res

    async def run_async(self):
        fm = self._read_frontmatter()
        scorer_type = fm.get("scorer", "exact_match")
        self.require_judge(scorer_type)

        # Load dataset
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
            raise ValueError(f"No dataset found at {dataset_path}. A dataset is required for Evaluation loops.")

        # Concurrency bound from config (same knob as StressRunner uses)
        max_parallel = self.config.stress.get("max_parallel", self.config.stress.get("concurrency", 10))
        semaphore = asyncio.Semaphore(max_parallel)

        # Fire all evaluation tasks concurrently, bounded by the semaphore
        tasks = [self._evaluate_item(item, scorer_type, semaphore) for item in dataset]
        results = await asyncio.gather(*tasks)

        # Aggregate results
        total_score = sum(r.score for r in results)
        passed_count = sum(1 for r in results if r.passed)
        total_items = len(results)

        avg_score = total_score / total_items if total_items > 0 else 0.0

        threshold = getattr(self, 'pass_threshold', 0.8)
        self.results.append(
            EvaluationResult(
                metric=f"aggregate_{scorer_type}",
                score=avg_score,
                passed=(avg_score >= threshold),
                details=f"Passed {passed_count}/{total_items} evaluation items (concurrency={max_parallel})."
            )
        )
