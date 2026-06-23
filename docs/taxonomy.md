# Loop Taxonomy

AI-Testing-Loops organizes its 100 loops into 6 categories and 16 subdomains.

## Categories

| Category | Count | Focus |
|----------|-------|-------|
| **Evaluation** | 25 | Measuring AI system quality, accuracy, and capabilities |
| **Guardrails** | 20 | Enforcing safety, compliance, and operational boundaries |
| **Stress Testing** | 15 | Finding performance limits, bottlenecks, and failure thresholds |
| **QA** | 15 | Regression testing, CI/CD integration, and quality monitoring |
| **Red Team / Security** | 15 | Adversarial testing against OWASP LLM Top 10 threats |
| **Reliability / Chaos** | 10 | Fault injection, failover, and resilience verification |

## Subdomains

| Subdomain | Aliases | Description |
|-----------|---------|-------------|
| `llm-evaluation` | `evaluation`, `evals` | Core LLM capability testing (reasoning, code, math) |
| `rag-evaluation` | `rag-testing` | Retrieval-Augmented Generation quality metrics |
| `agent-evaluation` | `agent-testing` | Agent tool use, planning, and task completion |
| `guardrails` | `safety-guardrails`, `input-guardrails`, `output-guardrails` | Input/output safety filters and policy enforcement |
| `stress-testing` | `load-testing`, `performance-testing` | Performance under load, concurrency, and resource pressure |
| `qa-testing` | `quality-assurance`, `regression-testing` | Regression detection, CI/CD gates, drift monitoring |
| `red-teaming` | `adversarial-testing`, `security-testing` | Adversarial attack simulation and defense validation |
| `prompt-security` | `prompt-injection`, `jailbreak-testing` | Prompt injection and jailbreak resistance testing |
| `reliability-engineering` | `chaos-engineering`, `fault-tolerance` | Fault injection and system resilience testing |
| `bias-fairness` | `fairness-testing` | Demographic parity, equalized odds, counterfactual testing |
| `hallucination-detection` | `factuality-testing` | Factual grounding and misinformation detection |
| `multi-agent-testing` | `orchestration-testing` | Multi-agent coordination, routing, and failure propagation |
| `memory-testing` | `state-management-testing` | Context retention, cross-session recall, memory corruption |
| `tool-use-testing` | `function-calling-testing` | Function calling accuracy, argument validation |
| `compliance-testing` | `governance-testing` | Supply chain, license, and regulatory compliance |
| `observability` | `monitoring`, `tracing` | Latency tracking, SLO compliance, cost monitoring |

## Framework Coverage

### OWASP LLM Top 10 (2025)
All 10 categories have dedicated loops. See [mappings/owasp-llm/](../mappings/owasp-llm/) for details.

### NIST AI RMF
All 4 functions (Govern, Map, Measure, Manage) are covered. See [mappings/nist-ai-rmf/](../mappings/nist-ai-rmf/) for details.

### MITRE ATLAS
Key adversarial ML techniques mapped to red team loops. See [mappings/mitre-atlas/](../mappings/mitre-atlas/) for details.

### Tool Ecosystem Coverage

| Tool/Framework | Loops Using It |
|----------------|----------------|
| DeepEval | Evaluation loops 1-25 |
| Promptfoo | Red team loops 76-90 |
| RAGAS | RAG evaluation loops 1-3 |
| NeMo Guardrails | Guardrail loops 28, 30, 31, 36, 43 |
| Guardrails AI | Guardrail loops 26, 29, 34, 38 |
| LlamaGuard | Guardrail loops 27, 35 |
| k6 / Locust | Stress testing loops 46-49 |
| Garak | Red team loops 76-82 |
| DeepTeam | Red team loops 78, 79, 82 |
