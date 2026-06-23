# Getting Started with the AI Evaluation Engine

This evaluation framework provides production-grade testing loops for LLM applications. It supports everything from simple RAG evaluations to complex multi-turn Red Teaming and load/stress testing.

## Prerequisites

- Python 3.9+
- Docker (required if running `code_exec` evaluation loops)

## 1. Installation

Clone the repository and install dependencies:
```bash
git clone https://github.com/0xnotdev/eval_engine.git
cd eval_engine/AI-Testing-Loops
pip install -r requirements.txt
```

## 2. Configuration (`config.yaml`)

Before running loops, you need to configure your adapters. Create a `config.yaml` file in your working directory. 

Here is an example configuring a local Ollama instance as the target, and OpenAI's GPT-4o as the judge:

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

## 3. Running a Loop

To run an evaluation loop, simply execute the `agent.py` script located inside its directory.

For example, to run the RAG Faithfulness evaluation:
```bash
python loops/evaluating-rag-faithfulness/scripts/agent.py --target "http://localhost:11434/v1/chat/completions" --config config.yaml
```

*Note: The `--target` CLI argument is mostly legacy; `config.yaml` is the preferred way to configure the target adapter.*

## 4. Validating Loops

To ensure the integrity of a loop structure (especially if you modify it), use the validation tool:
```bash
python tools/validate-loop.py loops/evaluating-rag-faithfulness
```

## 5. Reviewing Results

Upon completion, the loop runner will print a summary table to the console and generate two files:
1. `results.json`: Detailed execution metrics and inputs/outputs.
2. `junit.xml`: A standard JUnit XML file that can be ingested by CI/CD platforms (like GitHub Actions, Jenkins, or GitLab CI).
