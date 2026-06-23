# OWASP LLM Top 10 (2025) Coverage

This document maps AI-Testing-Loops to the OWASP Top 10 for LLM Applications.

> **How to read this table:** "Mapped" means one or more loops exist whose
> tests exercise this OWASP category. This is a **tagging exercise and a
> starting point** for auditor conversations — it is **not** a certified
> control verification. Run the listed loops against your target and use the
> generated reports as evidence; the coverage claim is only as good as your
> execution results.

## Coverage Matrix

| OWASP ID | Category | Risk Level | Loops | Mapped? |
|----------|----------|------------|-------|---------|
| LLM01 | Prompt Injection | Critical | 76, 77, 78, 79, 80, 42 | ✅ Yes |
| LLM02 | Sensitive Information Disclosure | High | 26, 81, 84 | ✅ Yes |
| LLM03 | Supply Chain Vulnerabilities | High | 75, 90 | ✅ Yes |
| LLM04 | Data and Model Poisoning | High | 86 | ✅ Yes |
| LLM05 | Improper Output Handling | Medium | 27, 29, 35 | ✅ Yes |
| LLM06 | Excessive Agency | Critical | 31, 36, 83, 89, 96 | ✅ Yes |
| LLM07 | System Prompt Leakage | High | 30, 82 | ✅ Yes |
| LLM08 | Vector and Embedding Weaknesses | Medium | 37, 45, 87, 93 | ✅ Yes |
| LLM09 | Misinformation | High | 15, 34, 38, 72 | ✅ Yes |
| LLM10 | Unbounded Consumption | Medium | 32, 41, 44, 85 | ✅ Yes |

## Detailed Mapping

### LLM01: Prompt Injection

Direct and indirect prompt injection attacks that override system instructions.

| Loop | Type | Description |
|------|------|-------------|
| [redteam-direct-prompt-injection-attack](../../loops/redteam-direct-prompt-injection-attack/) | Red Team | Direct injection payloads |
| [redteam-indirect-prompt-injection-via-documents](../../loops/redteam-indirect-prompt-injection-via-documents/) | Red Team | Injection via RAG documents |
| [redteam-multi-turn-escalation-jailbreak](../../loops/redteam-multi-turn-escalation-jailbreak/) | Red Team | Multi-turn escalation |
| [redteam-persona-roleplay-jailbreak](../../loops/redteam-persona-roleplay-jailbreak/) | Red Team | Persona-based bypass |
| [redteam-encoding-obfuscation-bypass](../../loops/redteam-encoding-obfuscation-bypass/) | Red Team | Encoded payload bypass |
| [guardrail-detecting-encoded-payload-obfuscation](../../loops/guardrail-detecting-encoded-payload-obfuscation/) | Guardrail | Defense against encoded payloads |

### LLM02: Sensitive Information Disclosure

Unintended exposure of PII, credentials, or confidential data.

| Loop | Type | Description |
|------|------|-------------|
| [guardrail-blocking-pii-leakage](../../loops/guardrail-blocking-pii-leakage/) | Guardrail | PII detection and blocking |
| [redteam-sensitive-information-extraction](../../loops/redteam-sensitive-information-extraction/) | Red Team | Data extraction attacks |
| [redteam-cross-session-data-leakage](../../loops/redteam-cross-session-data-leakage/) | Red Team | Cross-session leakage |

### LLM03: Supply Chain Vulnerabilities

Compromised models, packages, or pipeline dependencies.

| Loop | Type | Description |
|------|------|-------------|
| [qa-supply-chain-dependency-vulnerability-scanning](../../loops/qa-supply-chain-dependency-vulnerability-scanning/) | QA | CVE scanning |
| [redteam-supply-chain-model-integrity-verification](../../loops/redteam-supply-chain-model-integrity-verification/) | Red Team | Model provenance verification |

### LLM06: Excessive Agency

Autonomous actions beyond authorized scope.

| Loop | Type | Description |
|------|------|-------------|
| [guardrail-preventing-excessive-agency](../../loops/guardrail-preventing-excessive-agency/) | Guardrail | Action authorization |
| [guardrail-blocking-unauthorized-tool-execution](../../loops/guardrail-blocking-unauthorized-tool-execution/) | Guardrail | Tool whitelist enforcement |
| [redteam-excessive-agency-privilege-escalation](../../loops/redteam-excessive-agency-privilege-escalation/) | Red Team | Privilege escalation attacks |
| [redteam-tool-misuse-unintended-side-effects](../../loops/redteam-tool-misuse-unintended-side-effects/) | Red Team | Tool misuse attacks |
| [chaos-agent-infinite-loop-detection-and-circuit-breaking](../../loops/chaos-agent-infinite-loop-detection-and-circuit-breaking/) | Chaos | Infinite loop detection |

## References

- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/)
- [OWASP LLM AI Security and Governance Checklist](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
