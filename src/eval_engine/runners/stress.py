import asyncio
import time
from .base import BaseRunner, EvaluationResult

class StressRunner(BaseRunner):
    """Runner for concurrent load and stress testing."""
    
    async def run_async(self):
        # Simulated stress test logic using asyncio.gather
        concurrency = 10
        
        start_t = time.time()
        tasks = [self._send_payload({"messages": [{"role": "user", "content": "Stress test"}], "stream": False}) for _ in range(concurrency)]
        responses = await asyncio.gather(*tasks)
        end_t = time.time()
        
        duration = end_t - start_t
        throughput = concurrency / duration if duration > 0 else 0
        
        successes = sum(1 for r in responses if "error" not in r)
        
        self.results.append(
            EvaluationResult(
                metric="throughput_req_sec",
                score=throughput,
                passed=throughput > 5.0,
                details=f"Processed {successes}/{concurrency} requests in {duration:.2f}s"
            )
        )
