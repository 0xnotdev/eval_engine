---
name: qa-latency-slo-compliance-monitoring
description: >-
  Track P50 P95 and P99 latency percentiles against defined Service Level Objectives with automated breach alerting and dashboards
domain: ai-testing
subdomain: observability
tags:
  - latency
  - slo
  - p50
  - p95
  - p99
  - monitoring
  - alerting
version: '1.0'
author: ai-testing-loops
license: Apache-2.0
nist_ai_rmf:
  - MANAGE-3
requires: []
---
# Qa Latency Slo Compliance Monitoring

## Overview

Track P50 P95 and P99 latency percentiles against defined Service Level Objectives with automated breach alerting and dashboards. This loop provides a structured workflow and automation scripts to systematically verify the target's behavior, ensuring it meets production quality standards.

## When to Use

- When developing or modifying LLM components related to observability
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
