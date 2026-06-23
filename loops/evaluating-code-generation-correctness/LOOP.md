---
name: evaluating-code-generation-correctness
description: >-
  Validate functional correctness of LLM-generated code using HumanEval and MBPP-style test suite execution with pass@k metrics
domain: ai-testing
subdomain: llm-evaluation
tags:
  - code-generation
  - humaneval
  - mbpp
  - swe-bench
  - functional-correctness
version: '1.0'
author: ai-testing-loops
license: Apache-2.0
scorer: code_exec
nist_ai_rmf:
  - MEASURE-1
---
# Evaluating Code Generation Correctness

## Overview

Validate functional correctness of LLM-generated code using HumanEval and MBPP-style test suite execution with pass@k metrics. This loop provides a structured workflow and automation scripts to systematically verify the target's behavior, ensuring it meets production quality standards.

## When to Use

- When developing or modifying LLM components related to llm-evaluation
- During CI/CD pipelines as an automated gate
- Before deploying new model versions or system prompts

## Prerequisites

- Python 3.9+
- Relevant API access for the target system

```bash
pip install -r requirements.txt
```

## Objectives

- Systematically verify the behavior using automated metrics
- Identify and document failures or deviations from expected results
- Ensure regressions are caught early in the development cycle

## Workflow

### 1. Configure the Target

Set up the environment variables and target endpoints.

```bash
export TARGET_ENDPOINT="http://localhost:8000/api/chat"
```

### 2. Execute the Loop

Run the automated agent to perform the test.

```python
# See scripts/agent.py for full implementation
import subprocess
result = subprocess.run(["python", "scripts/agent.py", "--target", "http://localhost:8000/api/chat"])
```

### 3. Analyze Results

Review the generated report for failures.

```bash
cat results.json
```

## Validation Criteria

- [ ] Loop executed without unexpected runtime errors
- [ ] Results captured all required metrics
- [ ] Evaluation passed defined quality thresholds
