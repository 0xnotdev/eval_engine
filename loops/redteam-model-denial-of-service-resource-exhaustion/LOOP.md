---
name: redteam-model-denial-of-service-resource-exhaustion
description: >-
  Craft inputs designed to maximize token consumption compute time or trigger infinite generation loops to test resource exhaustion defenses
domain: ai-testing
subdomain: red-teaming
tags:
  - dos
  - resource-exhaustion
  - token-bomb
  - infinite-generation
  - abuse
version: '1.0'
author: ai-testing-loops
license: Apache-2.0
scorer: llm_judge
owasp_llm:
  - LLM10
mitre_atlas:
  - AML.T0040
---
# Redteam Model Denial Of Service Resource Exhaustion

> **Authorized Use Only:** This is a red-team loop. Run these adversarial probes only against LLM applications and endpoints you own or are explicitly authorized to test.

## Overview

Craft inputs designed to maximize token consumption compute time or trigger infinite generation loops to test resource exhaustion defenses. This loop provides a structured workflow and automation scripts to systematically verify the target's behavior, ensuring it meets production quality standards.

## When to Use

- When developing or modifying LLM components related to red-teaming
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
