#!/usr/bin/env python3
"""Loop automation script."""
import sys
import argparse
from pathlib import Path

# Dynamically load the core SDK
try:
    # Try resolving relative to loop directory
    sdk_path = str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    if sdk_path not in sys.path:
        sys.path.insert(0, sdk_path)
    from eval_engine.runners.evaluation import EvaluationRunner
except ImportError as e:
    print(f"Error: Core SDK not found. Make sure src/eval_engine is accessible. {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run evaluating-agent-step-efficiency loop")
    parser.add_argument("--target", required=True, help="Target API endpoint")
    parser.add_argument("--config", help="Optional config overrides", default="config.yaml")
    args = parser.parse_args()

    # Real execution engine
    runner = EvaluationRunner(
        loop_name="evaluating-agent-step-efficiency",
        tags=['agent', 'efficiency', 'step-count', 'deepeval', 'optimization'],
        target_endpoint=args.target
    )
    results = runner.execute()
    runner.save_report("results.json")

if __name__ == "__main__":
    main()
