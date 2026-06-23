---
name: evaluating-rag-faithfulness
description: >-
  Verify generated answers are factually grounded in retrieved context without hallucinated claims using RAGAS faithfulness scoring
domain: ai-testing
subdomain: rag-evaluation
scorer: llm_judge
tags:
  - rag
  - faithfulness
  - hallucination
  - ragas
  - deepeval
version: '1.0'
author: ai-testing-loops
license: Apache-2.0
owasp_llm:
  - LLM09
nist_ai_rmf:
  - MEASURE-2.6
---
# Evaluating Rag Faithfulness

## Overview

Verify generated answers are factually grounded in retrieved context without hallucinated claims using RAGAS faithfulness scoring. This loop provides a structured workflow and automation scripts to systematically verify the target's behavior, ensuring it meets production quality standards.

## When to Use

- When developing or modifying LLM components related to rag-evaluation
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
