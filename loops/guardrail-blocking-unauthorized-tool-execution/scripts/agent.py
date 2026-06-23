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
    from eval_engine.runners.guardrails import GuardrailsRunner
except ImportError as e:
    print(f"Error: Core SDK not found. Make sure src/eval_engine is accessible. {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run guardrail-blocking-unauthorized-tool-execution loop")
    parser.add_argument("--target", required=True, help="Target API endpoint")
    parser.add_argument("--config", help="Optional config overrides", default="config.yaml")
    parser.add_argument("--dataset", help="Path to custom dataset JSONL file", default=None)
    args = parser.parse_args()

    # Real execution engine
    runner = GuardrailsRunner(
        loop_name="guardrail-blocking-unauthorized-tool-execution",
        tags=['tool-whitelist', 'authorization', 'execution-rails', 'nemo-guardrails', 'agent-safety'],
        target_endpoint=args.target,
        config_path=args.config,
        dataset_override=args.dataset
    )
    results = runner.execute()
    runner.save_report("results.json")
    runner.save_junit_xml("junit.xml")

if __name__ == "__main__":
    main()
