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
        # Call the parent implementation first to populate framework_mappings,
        # requires, and pass_threshold.
        super()._read_frontmatter()

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

    async def _evaluate_item(self, item: dict, scorer_type: str, semaphore: asyncio.Semaphore):
        """Evaluate a single adversarial item (possibly multi-turn), bounded by semaphore."""
        async with semaphore:
            inputs = item.get("input", [])
            if isinstance(inputs, str):
                inputs = [inputs]  # Normalize to list of turns

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

            # Score based on the final actual response (or whole conversation)
            scorer = get_scorer(
                scorer_type,
                judge_adapter=self.judge_adapter,
                rubric=rubric,
                session=self.session
            )

            score_res = await scorer.score(expected, actual, latency_ms=latency_sum)
            return score_res

    async def run_async(self):
        fm = self._read_frontmatter()
        scorer_type = fm.get("scorer", "llm_judge")  # Default to judge for red team
        self.require_judge(scorer_type)

        # Load dataset via the shared BYOD-aware loader
        dataset = self._load_dataset()

        if not dataset:
            raise ValueError(f"No dataset found. A dataset is required for Red Team loops. "
                             f"Pass --dataset <path> or place dataset.example.jsonl in the loop's references/ directory.")

        # Concurrency bound from config
        max_parallel = self.config.stress.get("max_parallel", self.config.stress.get("concurrency", 10))
        semaphore = asyncio.Semaphore(max_parallel)

        # Fire all adversarial tests concurrently, bounded by semaphore.
        # Multi-turn conversations within each item remain sequential (you need
        # the model's reply to turn N before sending turn N+1).
        tasks = [self._evaluate_item(item, scorer_type, semaphore) for item in dataset]
        results = await asyncio.gather(*tasks)

        # Aggregate
        total_score = sum(r.score for r in results)
        passed_count = sum(1 for r in results if r.passed)
        total_items = len(results)

        avg_score = total_score / total_items if total_items > 0 else 0.0

        threshold = getattr(self, 'pass_threshold', 0.8)
        self.results.append(
            EvaluationResult(
                metric=f"redteam_resistance_{scorer_type}",
                score=avg_score,
                passed=(avg_score >= threshold),
                details=f"Resisted {passed_count}/{total_items} adversarial attacks (concurrency={max_parallel})."
            )
        )
