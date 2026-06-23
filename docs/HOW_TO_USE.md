# How to Use AI-Testing-Loops

This guide explains how to use the AI-Testing-Loops framework in a production environment. Whether you are an AI Developer, QA Engineer, or Red Teamer, this repository provides a unified turn-key software product for rigorous AI auditing.

## 1. Setup & Installation

Clone the repository and install the Core Execution Engine dependencies. This gives you access to the universal LLM metric runners, asynchronous stress testers, and rich terminal reporting.

```bash
git clone https://github.com/0xnotdev/eval_engine.git
cd eval_engine
pip install -r requirements.txt
```

## 2. Browsing for the Right Loop

The framework contains 100 loops categorized into 6 domains. Depending on your role, you will pick different loops:

- **AI Developers:** Focus on the **Evaluation Loops** (`evaluating-rag-context-relevance`, `evaluating-agent-task-completion`) to ensure feature correctness before merging PRs.
- **QA Engineers:** Focus on the **Stress Testing Loops** and **QA Loops** (`stress-testing-concurrent-api-load`, `qa-golden-dataset-assertion-testing`) to catch latency cliffs and regressions.
- **Red Teamers:** Focus on the **Red Team Loops** (`redteam-direct-prompt-injection-attack`, `redteam-excessive-agency-privilege-escalation`) to break safety guardrails.

*Tip: Read the `LOOP.md` inside any loop's directory to see exactly what framework (OWASP, NIST) it maps to.*

## 3. Executing a Loop Locally

Once you have identified the loop you want to run, point its `agent.py` script directly at your AI application's target endpoint. 

The script will automatically dynamically load the Core SDK (`src/eval_engine/`), generate the payloads, send the requests, evaluate the responses via LLM-as-a-judge (or custom assertions), and generate a report.

```bash
# Example: Testing if your RAG pipeline hallucinates
python loops/evaluating-rag-faithfulness/scripts/agent.py --target http://staging.your-app.com/api/chat
```

### The Output
The terminal will display a rich, formatted table detailing exactly which metrics passed and failed:

```text
Starting Loop: evaluating-rag-faithfulness
Target: http://staging.your-app.com/api/chat

Report saved to: results.json
                   Results: evaluating-rag-faithfulness                   
+-----------------------------------------------------------------------------+
| Metric                  | Score | Passed | Details                          |
|-------------------------+-------+--------+----------------------------------|
| rag_score               |  0.85 |  PASS  | Evaluated rag metric via         |
|                         |       |        | LLM-as-a-judge                   |
| faithfulness_score      |  0.40 |  FAIL  | Model hallucinated facts not in  |
|                         |       |        | the retrieved context            |
+-----------------------------------------------------------------------------+
```
A complete JSON payload will also be saved to `results.json` in your current directory.

## 4. Integration into CI/CD

To make the most of AI-Testing-Loops, you should integrate these tests as strict release gates in your CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI).

This ensures that no bad code or vulnerable prompts ever make it to production.

**Example GitHub Action:**
```yaml
name: Production AI Quality Gate
on: [push, pull_request]

jobs:
  run-ai-evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install Eval Engine
        run: pip install -r requirements.txt
        
      - name: Run PII Leakage Guardrail Test
        run: python loops/guardrail-blocking-pii-leakage/scripts/agent.py --target ${{ secrets.STAGING_API_URL }}
        
      - name: Assert Zero Leakage
        run: |
          python -c "
          import json, sys
          results = json.load(open('results.json'))
          if results['pass_rate'] < 1.0:
              print('PII Leakage Detected! Blocking Deployment.')
              sys.exit(1)
          print('Safety Check Passed.')
          "
```

## 5. Customizing the Configuration (`config.yaml`)

You can override standard evaluation settings and configure your target and judge adapters by passing a config YAML to the runner:

```bash
python loops/qa-golden-dataset-assertion-testing/scripts/agent.py \
    --target http://your-app.com/api/chat \
    --config config.yaml
```

**Adapter Configuration Example (`config.yaml`):**

A full, copy-pasteable template lives at [`config.example.yaml`](../config.example.yaml) in the repo root. The essentials:

```yaml
target:
  type: "openai_compatible"
  kwargs:
    endpoint: "http://localhost:11434/v1/chat/completions"
    model: "llama3"

judge:
  type: "openai_compatible"
  kwargs:
    endpoint: "https://api.openai.com/v1/chat/completions"
    model: "gpt-4o"
  headers:
    # Never hardcode a key. ${VAR} is resolved from the environment at load time.
    Authorization: "Bearer ${OPENAI_API_KEY}"

stress:
  concurrency: 50
  max_parallel: 10
```

> **Note:** The `judge:` section is **required** for any loop whose `LOOP.md`
> declares `scorer: llm_judge` (this includes every red-team loop and most
> evaluation loops). If it is missing, the runner now fails fast at startup
> with an actionable error instead of silently scoring every item `0.0`. Set
> the key in your environment: `export OPENAI_API_KEY="sk-..."`.

The Core SDK will automatically absorb your configurations, adjust concurrency limits, switch evaluator models, and dynamically map the loops to their appropriate `dataset.example.jsonl` files.

## 6. Bring Your Own Dataset

Every loop includes a bundled `dataset.example.jsonl` with 15-20 rows of sample data. In production, you should test your AI against your own real-world data.

You can override the example dataset by passing the `--dataset` flag to any agent script:

```bash
python loops/evaluating-summarization-quality/scripts/agent.py \
    --target http://your-app.com/api/chat \
    --dataset /path/to/your/custom_dataset.jsonl
```

If you do not pass a dataset, the runner will use the bundled example and log a warning: `⚠ Using bundled example dataset (20 rows). Pass --dataset to use your own.`

### Dataset Format
Datasets must be in JSON Lines (`.jsonl`) format. Each row must be a valid JSON object containing at minimum the `input` field. Evaluation loops usually require an `expected` field, and LLM-as-a-judge loops often require a `rubric` field.

Example `custom_dataset.jsonl`:
```json
{"input": "Summarize this: The quick brown fox jumps over the lazy dog.", "expected": "A fox jumps over a dog.", "rubric": "Must mention the fox and the dog."}
{"input": "Summarize this: A loud noise woke me up at midnight.", "expected": "A noise interrupted sleep at midnight.", "rubric": "Must mention noise and midnight."}
```
