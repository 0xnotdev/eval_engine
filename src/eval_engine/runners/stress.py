import asyncio
import time
from .base import BaseRunner, EvaluationResult

class StressRunner(BaseRunner):
    """Runner for concurrent load and stress testing."""
    
    async def run_async(self):
        # Load profile
        import yaml
        from pathlib import Path
        load_profile_path = Path("loops") / self.loop_name / "references" / "load-profile.yaml"
            
        profile = {}
        if load_profile_path.exists():
            with open(load_profile_path, "r", encoding="utf-8") as f:
                profile = yaml.safe_load(f) or {}
                
        # Merge with config.yaml overrides
        concurrency = self.config.stress.get("concurrency", profile.get("concurrency", 10))
        max_parallel = self.config.stress.get("max_parallel", profile.get("max_parallel", 10))
        payload_text = profile.get("payload", "Stress test payload. Please write a long response.")
        
        semaphore = asyncio.Semaphore(max_parallel)
        
        async def bounded_send(payload):
            async with semaphore:
                return await self._send_payload(payload)

        start_t = time.time()
        # Enable streaming to measure TTFT
        tasks = [bounded_send({"messages": [{"role": "user", "content": payload_text}], "stream": True}) for _ in range(concurrency)]
        responses = await asyncio.gather(*tasks)
        end_t = time.time()
        
        duration = end_t - start_t
        throughput = concurrency / duration if duration > 0 else 0
        
        successes = 0
        total_ttft = 0.0
        total_tokens = 0
        
        for r in responses:
            if isinstance(r, dict) and "error" not in r:
                successes += 1
                ttft = r.get("_ttft_ms")
                if ttft is not None:
                    total_ttft += ttft
                
                text = r.get("_adapter_text", "")
                # Roughly estimate tokens as words * 1.3
                total_tokens += len(text.split()) * 1.3
                
        avg_ttft = (total_ttft / successes) if successes > 0 else 0.0
        tps = total_tokens / duration if duration > 0 else 0.0
        
        self.results.append(
            EvaluationResult(
                metric="throughput_req_sec",
                score=throughput,
                passed=throughput > 0.5 and successes > (concurrency * 0.8), # Pass if 80% success
                details=f"Processed {successes}/{concurrency} requests in {duration:.2f}s"
            )
        )
        
        self.results.append(
            EvaluationResult(
                metric="tokens_per_sec",
                score=tps,
                passed=tps > 10.0,
                details=f"Generated {int(total_tokens)} tokens at {tps:.2f} TPS"
            )
        )
        
        self.results.append(
            EvaluationResult(
                metric="avg_ttft_ms",
                score=avg_ttft,
                passed=avg_ttft > 0 and avg_ttft < 2000.0,
                details=f"Average TTFT was {avg_ttft:.2f}ms"
            )
        )
