# NIST AI Risk Management Framework Alignment

This document maps AI-Testing-Loops to the NIST AI RMF functions and categories.

## Function Coverage

| Function | Description | Loop Coverage |
|----------|-------------|---------------|
| **GOVERN** | Policies, accountability, and organizational practices | Guardrail loops (26-45), Compliance (75) |
| **MAP** | Context, capabilities, and risk identification | Taxonomy docs, framework mappings |
| **MEASURE** | Assessment of trustworthiness characteristics | Evaluation loops (1-25), Stress tests (46-60) |
| **MANAGE** | Monitoring, response, and continuous improvement | QA loops (61-75), Chaos loops (91-100) |

## Detailed Alignment

### GOVERN — Establishing AI Governance

| NIST Category | Description | Relevant Loops |
|---------------|-------------|----------------|
| GOVERN-1 | Legal and regulatory requirements | 39, 40, 75 |
| GOVERN-2 | Accountability structures | 31, 36 |
| GOVERN-3 | Workforce diversity and domain expertise | 67 |
| GOVERN-4 | Organizational AI risk culture | 28, 33, 34 |
| GOVERN-5 | Processes for AI lifecycle | 65, 66 |
| GOVERN-6 | Policies and procedures | 26, 27, 29, 30 |

### MEASURE — Evaluating AI Systems

| NIST Category | Description | Relevant Loops |
|---------------|-------------|----------------|
| MEASURE-1 | Appropriate methods and metrics | 1-6, 17, 19, 24 |
| MEASURE-2 | AI systems evaluated for trustworthiness | 7-11, 15, 16 |
| MEASURE-2.6 | Post-deployment monitoring | 66, 70 |
| MEASURE-2.7 | AI system security and resilience | 46-60, 76-90 |
| MEASURE-3 | Processes for tracking metrics | 61-64, 71, 74 |
| MEASURE-4 | Feedback and human oversight | 67, 73 |

### MANAGE — Managing AI Risks

| NIST Category | Description | Relevant Loops |
|---------------|-------------|----------------|
| MANAGE-1 | AI risks based on assessments | 91-100 |
| MANAGE-2 | Strategies to maximize benefits | 63, 65 |
| MANAGE-3 | AI risks and benefits monitored | 66, 70, 44 |
| MANAGE-4 | Risk treatments applied | 91-100 |
| MANAGE-4.1 | Post-deployment monitoring | 66, 70, 71 |

## Trustworthiness Characteristics

| Characteristic | NIST Definition | Loop Categories |
|----------------|-----------------|-----------------|
| **Valid & Reliable** | System performs as intended | Evaluation (1-25), QA (61-75) |
| **Safe** | Does not endanger human life | Guardrails (26-45) |
| **Secure & Resilient** | Resists attacks, recovers from failures | Red Team (76-90), Chaos (91-100) |
| **Accountable & Transparent** | Decisions can be explained | Observability, logging loops |
| **Explainable & Interpretable** | Outputs can be understood | Evaluation loops with rubrics |
| **Privacy-Enhanced** | Protects personal information | PII loops (26, 81, 84) |
| **Fair — Bias Managed** | Equitable treatment across demographics | Toxicity/bias loops (15, 27) |

## References

- [NIST AI Risk Management Framework](https://www.nist.gov/artificial-intelligence/risk-management-framework)
- [NIST AI 100-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)
