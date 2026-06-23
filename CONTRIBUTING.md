# Contributing to AI-Testing-Loops

Thank you for your interest in contributing! This project aims to be the definitive collection of production-grade AI testing loops.

## How to Add a New Loop

1. **Fork** this repository and create a feature branch.
2. **Create a directory** under `loops/` using kebab-case, verb-first naming:
   ```
   loops/your-loop-name/
   ├── LOOP.md              # Required — primary definition
   ├── LICENSE               # Required — Apache-2.0 copy
   ├── references/
   │   ├── api-reference.md  # Tool/library command reference
   │   └── standards.md      # Framework mapping rationale
   └── scripts/
       └── agent.py          # Automation script (stdlib-only preferred)
   ```
3. **Write your LOOP.md** with valid YAML frontmatter (see below) and all required sections.
4. **Run the validator** locally:
   ```bash
   python tools/validate-loop.py loops/your-loop-name/LOOP.md
   ```
5. **Submit a Pull Request** against `main`.

## LOOP.md Quality Checklist

Before submitting, ensure your loop meets these standards:

- [ ] YAML frontmatter has all required fields (`name`, `description`, `domain`, `subdomain`, `tags`, `version`, `author`, `license`, `pass_threshold`)
- [ ] `name` matches directory name, is kebab-case, max 64 characters
- [ ] `description` is ≥ 50 characters and keyword-rich for discovery
- [ ] `subdomain` is from the [allowed list](#allowed-subdomains)
- [ ] `pass_threshold` is defined in frontmatter (e.g., `0.8` or `1.0`)
- [ ] At least 2 `tags` provided
- [ ] `references/dataset.jsonl` exists and is populated if this is an evaluation, red-teaming, or guardrails loop
- [ ] Body contains: **When to Use**, **Prerequisites**, **Workflow** (numbered steps with code blocks)
- [ ] Workflow steps include runnable code (bash, Python, or YAML configs)
- [ ] `scripts/agent.py` wraps the workflow programmatically with argparse CLI
- [ ] `references/standards.md` maps to at least one framework (OWASP LLM, NIST AI RMF, MITRE ATLAS)
- [ ] `Validation Criteria` section has checkbox items for verifying the loop ran correctly

## Allowed Subdomains

| Subdomain | Aliases |
|-----------|---------|
| `llm-evaluation` | `evaluation`, `evals` |
| `rag-evaluation` | `rag-testing` |
| `agent-evaluation` | `agent-testing` |
| `guardrails` | `safety-guardrails`, `input-guardrails`, `output-guardrails` |
| `stress-testing` | `load-testing`, `performance-testing` |
| `qa-testing` | `quality-assurance`, `regression-testing` |
| `red-teaming` | `adversarial-testing`, `security-testing` |
| `prompt-security` | `prompt-injection`, `jailbreak-testing` |
| `reliability-engineering` | `chaos-engineering`, `fault-tolerance` |
| `bias-fairness` | `fairness-testing` |
| `hallucination-detection` | `factuality-testing` |
| `multi-agent-testing` | `orchestration-testing` |
| `memory-testing` | `state-management-testing` |
| `tool-use-testing` | `function-calling-testing` |
| `compliance-testing` | `governance-testing` |
| `observability` | `monitoring`, `tracing` |

## Code Style

- **Python scripts:** Follow PEP 8, use type hints, prefer stdlib-only dependencies.
- **YAML configs:** Use 2-space indentation, quote strings containing special characters.
- **Markdown:** Use ATX headings (`#`), fenced code blocks with language tags.

## Reporting Issues

- **Bug in a loop:** Use the "Improve Loop" issue template.
- **New loop request:** Use the "New Loop Request" issue template.
- **Security issue:** See [SECURITY.md](SECURITY.md).
