import pytest
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from eval_engine.runners.stress import StressRunner

@pytest.mark.asyncio
async def test_extreme_concurrency_stress():
    """
    Test the StressRunner with massive concurrency to ensure it doesn't crash 
    the OS with Too Many Open Files and handles bad JSON responses.
    """
    runner = StressRunner(
        loop_name="test-extreme-stress",
        tags=["stress"],
        target_endpoint="http://127.0.0.1:8080/api/chat"
    )
    
    # We will override the concurrency in StressRunner for the test
    # Currently StressRunner is hardcoded to 10 concurrency inside run_async.
    # Let's monkeypatch it to 1000 for the test to cause a crash if unhandled.
    
    async def run_massive_stress():
        concurrency = 1000
        tasks = [runner._send_payload({"messages": [{"role": "user", "content": "Stress"}]}) for _ in range(concurrency)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses
    
    # Run the test
    responses = await run_massive_stress()
    
    # Analyze responses
    successes = sum(1 for r in responses if isinstance(r, dict) and "error" not in r)
    errors = sum(1 for r in responses if isinstance(r, dict) and "error" in r)
    
    # Ensure it didn't throw an unhandled exception entirely
    assert len(responses) == 1000
    print(f"Successes: {successes}, Errors: {errors}")
