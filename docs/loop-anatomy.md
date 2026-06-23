# Loop Anatomy

Every loop in this repository follows a consistent, battle-tested structure designed for immediate usability in production CI/CD pipelines.

## Directory Structure

```
loops/<loop-name>/
├── LOOP.md              ← Primary definition
├── LICENSE              ← Apache 2.0
├── references/
│   ├── api-reference.md ← Tool/library command reference
│   └── standards.md     ← Framework mapping with rationale
└── scripts/
    └── agent.py         ← Automation script
```

## LOOP.md Structure

### 1. YAML Frontmatter

Every `LOOP.md` starts with YAML frontmatter containing metadata for discovery and validation:

```yaml
---
name: loop-name-in-kebab-case        # Required: max 64 chars
description: >-                       # Required: min 50 chars
  Detailed description for agent
  discovery and human understanding.
domain: ai-testing                    # Required: always "ai-testing"
subdomain: rag-evaluation             # Required: from allowed taxonomy
tags:                                 # Required: at least 2 tags
  - tag1
  - tag2
version: '1.0'                       # Required
author: contributor-name              # Required
license: Apache-2.0                   # Required
owasp_llm:                            # Optional: OWASP LLM Top 10 IDs
  - LLM09
nist_ai_rmf:                          # Optional: NIST AI RMF references
  - MEASURE-2.6
mitre_atlas:                          # Optional: MITRE ATLAS technique IDs
  - AML.T0048
---
```

### 2. Markdown Body

The body follows a standard section progression:

| Section | Required | Purpose |
|---------|----------|---------|
| `# Title` | Yes | H1 heading matching the loop name |
| `> Notice` | If red-team | Legal/authorized-use notice |
| `## Overview` | Recommended | What this tests and why it matters |
| `## When to Use` | **Yes** | Bullet list of trigger conditions |
| `## Prerequisites` | **Yes** | Tools, access, environment setup |
| `## Objectives` | Recommended | What success looks like |
| `## Framework Mapping` | Recommended | OWASP/NIST/ATLAS table |
| `## Workflow` | **Yes** | Numbered steps with code blocks |
| `## Tools & Resources` | Recommended | Links to frameworks/docs |
| `## Validation Criteria` | Recommended | Checkbox items for verification |

### 3. Workflow Steps

Each workflow step should include:
- A numbered heading (`### 1. Step Title`)
- Explanation of what this step accomplishes
- Runnable code block (```bash, ```python, or ```yaml)
- Expected output or interpretation guidance

## scripts/agent.py

Every loop includes an automation script that:
- Wraps the workflow steps programmatically
- Uses `argparse` for CLI interface
- Outputs results as JSON
- Prefers stdlib-only dependencies
- Includes a `main()` entry point

```python
#!/usr/bin/env python3
"""Loop automation script."""
import argparse
import json

class LoopAgent:
    def __init__(self, target: str):
        self.target = target
        self.results = []

    def run(self) -> dict:
        # Execute workflow steps
        return {"pass_rate": 0.0, "results": self.results}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", default="results.json")
    args = parser.parse_args()

    agent = LoopAgent(args.target)
    results = agent.run()

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
```

## references/standards.md

Maps the loop to industry frameworks with rationale:

```markdown
# Standards Mapping

## OWASP LLM Top 10
| ID | Name | Rationale |
|----|------|-----------|
| LLM09 | Misinformation | This loop tests for hallucinated content... |

## NIST AI RMF
| ID | Name | Rationale |
|----|------|-----------|
| MEASURE-2.6 | ... | ... |
```
