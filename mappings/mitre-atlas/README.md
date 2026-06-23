# MITRE ATLAS Technique Mapping

This document maps AI-Testing-Loops red team and security loops to MITRE ATLAS (Adversarial Threat Landscape for AI Systems) techniques.

## Technique Coverage

| ATLAS ID | Technique Name | Tactic | Loops |
|----------|---------------|--------|-------|
| AML.T0015 | Evade ML Model | Evasion | 80 |
| AML.T0020 | Poison Training Data | Persistence | 86 |
| AML.T0024 | Exfiltration via ML Inference API | Exfiltration | 81, 84 |
| AML.T0035 | ML Supply Chain Compromise | Initial Access | 75, 90 |
| AML.T0040 | ML Model Inference API Access | Reconnaissance | 85 |
| AML.T0042 | Verify Attack | Impact | 76-90 |
| AML.T0043 | Craft Adversarial Data | Resource Development | 87, 93 |
| AML.T0047 | ML Supply Chain Compromise | Initial Access | 90 |
| AML.T0048 | Infer Training Data | Collection | 81 |
| AML.T0051 | LLM Prompt Injection | Initial Access | 76, 77, 80 |
| AML.T0051.000 | Direct Prompt Injection | Initial Access | 76 |
| AML.T0051.001 | Indirect Prompt Injection | Initial Access | 77 |
| AML.T0054 | LLM Jailbreak | Privilege Escalation | 78, 79, 80 |
| AML.T0056 | LLM Meta Prompt Extraction | Collection | 82 |
| AML.T0057 | LLM Data Leakage | Exfiltration | 81, 84 |

## Tactic Coverage

| Tactic | Description | Loop Count |
|--------|-------------|------------|
| Reconnaissance | Gathering information about the AI system | 3 |
| Resource Development | Creating adversarial resources | 2 |
| Initial Access | Gaining initial access to the AI system | 5 |
| Persistence | Maintaining access to the AI system | 1 |
| Privilege Escalation | Gaining higher-level permissions | 3 |
| Defense Evasion | Avoiding detection | 2 |
| Collection | Gathering data from the AI system | 2 |
| Exfiltration | Stealing data from the AI system | 3 |
| Impact | Disrupting or degrading the AI system | 4 |

## Loop-to-Technique Mapping

### Red Team Loops

| Loop | Primary Technique | Secondary Techniques |
|------|-------------------|---------------------|
| redteam-direct-prompt-injection-attack | AML.T0051.000 | AML.T0042 |
| redteam-indirect-prompt-injection-via-documents | AML.T0051.001 | AML.T0043 |
| redteam-multi-turn-escalation-jailbreak | AML.T0054 | AML.T0051 |
| redteam-persona-roleplay-jailbreak | AML.T0054 | AML.T0051 |
| redteam-encoding-obfuscation-bypass | AML.T0015 | AML.T0054 |
| redteam-sensitive-information-extraction | AML.T0057 | AML.T0048 |
| redteam-system-prompt-extraction-attack | AML.T0056 | AML.T0057 |
| redteam-excessive-agency-privilege-escalation | AML.T0054 | — |
| redteam-cross-session-data-leakage | AML.T0024 | AML.T0057 |
| redteam-model-denial-of-service-resource-exhaustion | AML.T0040 | — |
| redteam-data-poisoning-training-pipeline | AML.T0020 | — |
| redteam-vector-embedding-adversarial-manipulation | AML.T0043 | AML.T0015 |
| redteam-authorization-bypass-bola-bfla | AML.T0054 | — |
| redteam-tool-misuse-unintended-side-effects | AML.T0054 | — |
| redteam-supply-chain-model-integrity-verification | AML.T0047 | AML.T0035 |

## References

- [MITRE ATLAS](https://atlas.mitre.org/)
- [MITRE ATLAS Navigator](https://atlas.mitre.org/navigator)
- [MITRE ATLAS Techniques](https://atlas.mitre.org/techniques)
