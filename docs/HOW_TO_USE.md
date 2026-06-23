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
    Authorization: "Bearer sk-proj-your-api-key"

stress:
  concurrency: 50
  max_parallel: 10
```

The Core SDK will automatically absorb your configurations, adjust concurrency limits, switch evaluator models, and dynamically map the loops to their appropriate `dataset.jsonl` files.
