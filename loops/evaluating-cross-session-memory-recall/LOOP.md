---
name: evaluating-cross-session-memory-recall
description: >-
  Verify long-term memory systems correctly retrieve and apply facts across separate conversation sessions using recall accuracy metrics
domain: ai-testing
subdomain: memory-testing
tags:
  - memory
  - cross-session
  - recall
  - long-term
  - mem0
version: '1.0'
author: ai-testing-loops
license: Apache-2.0
nist_ai_rmf:
  - MEASURE-2
---
# Evaluating Cross Session Memory Recall

## Overview

Verify long-term memory systems correctly retrieve and apply facts across separate conversation sessions using recall accuracy metrics. This loop provides a structured workflow and automation scripts to systematically verify the target's behavior, ensuring it meets production quality standards.

## When to Use

- When developing or modifying LLM components related to memory-testing
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
