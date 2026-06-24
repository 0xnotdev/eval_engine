# 🔬 AI-Testing-Loops

**100 production-grade testing loops for AI/LLM systems** — covering evaluation, guardrails, stress testing, QA, red-teaming, and reliability engineering.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Loops](https://img.shields.io/badge/Loops-100-brightgreen.svg)](#loop-inventory)
[![OWASP LLM](https://img.shields.io/badge/OWASP%20LLM%20Top%2010-Mapped-orange.svg)](#standards-coverage)
[![NIST AI RMF](https://img.shields.io/badge/NIST%20AI%20RMF-Aligned-purple.svg)](#standards-coverage)
[![MITRE ATLAS](https://img.shields.io/badge/MITRE%20ATLAS-Mapped-red.svg)](#standards-coverage)

---

## 🚀 What Is This?

AI-Testing-Loops is a **plug-and-play collection of 100 self-contained testing modules** designed for teams shipping production AI systems. Each "loop" is a complete, reusable testing recipe — with configuration templates, automation scripts, framework mappings, and validation criteria — that you can drop into your CI/CD pipeline, run locally, or adapt to your stack.

Think of it as the **OWASP Testing Guide, but for AI** — except every entry is executable, not just documentation.

### Who Is This For?

- **ML Engineers** shipping LLM-powered features who need systematic evaluation
- **Platform Teams** building AI infrastructure with reliability requirements
- **Security Engineers** red-teaming LLM applications before production
- **QA Teams** integrating AI testing into existing CI/CD pipelines
- **Engineering Managers** who need compliance evidence (OWASP, NIST, SOC2)

---

## 🛠️ Engine Capabilities

The testing loops are powered by a robust Python-based evaluation engine included in `src/eval_engine/`. It features:

- **Universal Provider Adapters:** Plug-and-play support for Anthropic and OpenAI-compatible endpoints via `config.yaml`.
- **Advanced Scorers:** 
  - **Docker-Isolated Code Execution:** Safely evaluate LLM-generated code (`CodeExecScorer`).
  - **LLM-as-a-Judge:** Flexible natural-language rubric evaluations (`LlmJudgeScorer`).
  - **Exact/Regex Match, Embedding Similarity, Latency SLO:** deterministic scorers for structured assertions.
- **Comprehensive Reporting & Stats:** Auto-generates detailed JSON and JUnit XML reports with pass rates, Wilson score confidence intervals, sample size bands, and built-in framework mappings (OWASP, NIST).
- **Bring Your Own Dataset (BYOD):** Run loops with your own data via the `--dataset` CLI override instead of relying on bundled examples.
- **Chaos Engineering:** Dynamic fault injectors (`vector_db_outage`, `memory_corruption`, `model_hot_swap`) seamlessly mutate requests before they hit your model.
- **Stress & Load Testing:** Configurable concurrency and rate limits driven by `load-profile.yaml` to test application boundaries.
- **Concurrent Runners:** `EvaluationRunner`, `RedTeamRunner`, `GuardrailsRunner`, and `ChaosRunner` process datasets in parallel (semaphore-bounded `asyncio.gather`), configurable via the `stress` block in `config.yaml`.
- **Pre-flight Checks:** Fails fast with clear instructions if required environment tools (like Docker or Judge models) are missing before execution begins.

> **A note on framework compatibility:** Loop tags reference well-known
> frameworks and tools (RAGAS, DeepEval, Presidio, NeMo Guardrails, LlamaGuard,
> k6, etc.) as **categorization labels** — they describe *what dimension* a
> loop tests (e.g., a `ragas`-tagged loop exercises faithfulness, the metric
> RAGAS popularized). The engine ships its **own self-contained scorer set**;
> it does not import or call those third-party libraries. If you need native
> RAGAS/DeepEval metrics, the scorer interface (`src/eval_engine/scorers/`)
> is designed to be extended — see [`docs/HOW_TO_USE.md`](docs/HOW_TO_USE.md).

---

## 📂 Repository Structure

```
AI-Testing-Loops/
├── README.md                    ← You are here
├── CONTRIBUTING.md              ← How to add loops
├── SECURITY.md                  ← Vulnerability disclosure
├── LICENSE                      ← Apache 2.0
├── CITATION.cff                 ← Academic citation
├── config.example.yaml          ← Copy to config.yaml & add your API key
├── pyproject.toml               ← pip install -e . for the engine
├── requirements.txt             ← Runtime dependencies
├── index.json                   ← Auto-generated loop catalog
│
├── loops/                       ← 100 testing loops
│   └── <loop-name>/
│       ├── LOOP.md              ← Primary definition (frontmatter + workflow)
│       ├── LICENSE              ← Apache 2.0
│       ├── references/
│       │   └── standards.md     ← Framework mapping rationale
│       └── scripts/
│           └── agent.py         ← Automation script
│
├── tools/
│   ├── validate-loop.py         ← Frontmatter + structure validator
│   └── README.md                ← Validator usage
│
├── docs/
│   ├── loop-anatomy.md          ← How loops are structured
│   └── taxonomy.md              ← Category taxonomy reference
│
├── mappings/
│   ├── owasp-llm/
│   │   └── README.md            ← OWASP LLM Top 10 coverage
│   ├── nist-ai-rmf/
│   │   └── README.md            ← NIST AI RMF alignment
│   └── mitre-atlas/
│       └── README.md            ← MITRE ATLAS technique mapping
│
├── tests/                       ← Unit & integration testing
│   ├── test_scorers.py
│   └── test_adapters.py
│
└── .github/
    ├── workflows/
    │   ├── validate-loops.yml   ← CI: validate on PR
    │   └── update-index.yml     ← CI: regenerate index.json
    └── ISSUE_TEMPLATE/
        ├── new-loop.md          ← Request a new loop
        └── improve-loop.md      ← Improve existing loop
```

---

## 🧬 Anatomy of a Loop

Every loop follows the same battle-tested structure:

```yaml
# LOOP.md Frontmatter
---
name: evaluating-rag-faithfulness           # kebab-case, verb-first
description: >-
  Verify generated answers are factually grounded in retrieved context
  without hallucinated claims using RAGAS faithfulness scoring.
domain: ai-testing                          # always "ai-testing"
subdomain: rag-evaluation                   # from allowed taxonomy
tags: [rag, faithfulness, hallucination, ragas, deepeval]
version: '1.0'
author: ai-testing-loops
license: Apache-2.0
owasp_llm: [LLM09]                         # OWASP LLM Top 10
nist_ai_rmf: [MEASURE-2.6]                 # NIST AI RMF
mitre_atlas: [AML.T0048]                   # MITRE ATLAS
---
```

### Body Sections

| Section | Purpose |
|---------|---------|
| **Overview** | What this loop tests and why it matters |
| **When to Use** | Trigger conditions for running this loop |
| **Prerequisites** | Tools, access, and environment setup |
| **Objectives** | What success looks like |
| **Workflow** | Step-by-step execution with runnable code |
| **Tools & Resources** | Links to frameworks and documentation |
| **Validation Criteria** | Checklist to confirm the loop ran correctly |

---

## 📊 Loop Inventory

### Evaluation Loops (25)

| # | Loop | Description |
|---|------|-------------|
| 1 | [evaluating-rag-context-relevance](loops/evaluating-rag-context-relevance/) | Measure retrieved document relevance to user queries |
| 2 | [evaluating-rag-faithfulness](loops/evaluating-rag-faithfulness/) | Verify answers are grounded in retrieved context |
| 3 | [evaluating-rag-answer-relevancy](loops/evaluating-rag-answer-relevancy/) | Assess response completeness against user questions |
| 4 | [evaluating-llm-reasoning-accuracy](loops/evaluating-llm-reasoning-accuracy/) | Benchmark multi-step reasoning on GPQA/ARC-AGI |
| 5 | [evaluating-code-generation-correctness](loops/evaluating-code-generation-correctness/) | Validate generated code with HumanEval/MBPP suites |
| 6 | [evaluating-mathematical-problem-solving](loops/evaluating-mathematical-problem-solving/) | Test competition-level math (AIME, MATH) |
| 7 | [evaluating-agent-task-completion](loops/evaluating-agent-task-completion/) | Measure agent end-to-end success rates |
| 8 | [evaluating-agent-tool-selection-accuracy](loops/evaluating-agent-tool-selection-accuracy/) | Verify correct tool selection per reasoning step |
| 9 | [evaluating-agent-argument-correctness](loops/evaluating-agent-argument-correctness/) | Validate tool call parameter accuracy |
| 10 | [evaluating-agent-plan-quality](loops/evaluating-agent-plan-quality/) | Score execution plan completeness and efficiency |
| 11 | [evaluating-agent-step-efficiency](loops/evaluating-agent-step-efficiency/) | Measure optimal step count without redundancy |
| 12 | [evaluating-conversation-completeness](loops/evaluating-conversation-completeness/) | Assess multi-turn intent resolution |
| 13 | [evaluating-knowledge-retention-across-turns](loops/evaluating-knowledge-retention-across-turns/) | Test fact retention across conversation turns |
| 14 | [evaluating-role-adherence-consistency](loops/evaluating-role-adherence-consistency/) | Verify persona maintenance throughout interaction |
| 15 | [evaluating-response-toxicity-scoring](loops/evaluating-response-toxicity-scoring/) | Score outputs for toxic/harmful language |
| 16 | [evaluating-output-format-compliance](loops/evaluating-output-format-compliance/) | Validate structured output schema conformance |
| 17 | [evaluating-summarization-quality](loops/evaluating-summarization-quality/) | Measure summary accuracy, coverage, conciseness |
| 18 | [evaluating-multi-modal-image-coherence](loops/evaluating-multi-modal-image-coherence/) | Assess multi-modal output coherence |
| 19 | [evaluating-semantic-similarity-scoring](loops/evaluating-semantic-similarity-scoring/) | Compute embedding similarity for regression detection |
| 20 | [evaluating-context-window-utilization](loops/evaluating-context-window-utilization/) | Test performance degradation at token limits |
| 21 | [evaluating-cross-session-memory-recall](loops/evaluating-cross-session-memory-recall/) | Verify long-term memory retrieval accuracy |
| 22 | [evaluating-multi-agent-orchestrator-routing](loops/evaluating-multi-agent-orchestrator-routing/) | Validate orchestrator task delegation |
| 23 | [evaluating-inter-agent-handoff-coherence](loops/evaluating-inter-agent-handoff-coherence/) | Assess context preservation during handoffs |
| 24 | [evaluating-custom-domain-rubric-geval](loops/evaluating-custom-domain-rubric-geval/) | Score outputs against custom rubrics via G-Eval |
| 25 | [evaluating-real-world-software-engineering](loops/evaluating-real-world-software-engineering/) | Test end-to-end GitHub issue resolution |

### Guardrail Loops (20)

| # | Loop | Description |
|---|------|-------------|
| 26 | [guardrail-blocking-pii-leakage](loops/guardrail-blocking-pii-leakage/) | Detect and block PII in inputs/outputs |
| 27 | [guardrail-filtering-toxic-content](loops/guardrail-filtering-toxic-content/) | Intercept hate speech and harmful content |
| 28 | [guardrail-enforcing-topic-boundaries](loops/guardrail-enforcing-topic-boundaries/) | Prevent off-topic engagement via dialogue rails |
| 29 | [guardrail-validating-output-schema](loops/guardrail-validating-output-schema/) | Enforce structured output conformance with retry |
| 30 | [guardrail-detecting-system-prompt-leakage](loops/guardrail-detecting-system-prompt-leakage/) | Block system prompt extraction attempts |
| 31 | [guardrail-preventing-excessive-agency](loops/guardrail-preventing-excessive-agency/) | Limit autonomous actions without authorization |
| 32 | [guardrail-rate-limiting-token-consumption](loops/guardrail-rate-limiting-token-consumption/) | Enforce per-user token/request limits |
| 33 | [guardrail-blocking-competitor-endorsement](loops/guardrail-blocking-competitor-endorsement/) | Prevent competitor product recommendations |
| 34 | [guardrail-enforcing-citation-requirements](loops/guardrail-enforcing-citation-requirements/) | Require source citations for generated claims |
| 35 | [guardrail-content-moderation-classification](loops/guardrail-content-moderation-classification/) | Classify content into safety categories |
| 36 | [guardrail-blocking-unauthorized-tool-execution](loops/guardrail-blocking-unauthorized-tool-execution/) | Prevent unapproved tool/API calls |
| 37 | [guardrail-enforcing-retrieval-source-filtering](loops/guardrail-enforcing-retrieval-source-filtering/) | Validate RAG sources are from approved origins |
| 38 | [guardrail-detecting-hallucinated-urls](loops/guardrail-detecting-hallucinated-urls/) | Verify URLs in outputs are not fabricated |
| 39 | [guardrail-enforcing-language-locale-compliance](loops/guardrail-enforcing-language-locale-compliance/) | Ensure outputs match required language/locale |
| 40 | [guardrail-blocking-medical-legal-financial-advice](loops/guardrail-blocking-medical-legal-financial-advice/) | Redirect unauthorized professional advice |
| 41 | [guardrail-input-length-validation](loops/guardrail-input-length-validation/) | Reject inputs exceeding safe token thresholds |
| 42 | [guardrail-detecting-encoded-payload-obfuscation](loops/guardrail-detecting-encoded-payload-obfuscation/) | Block base64/leetspeak/unicode obfuscation |
| 43 | [guardrail-enforcing-conversation-flow-logic](loops/guardrail-enforcing-conversation-flow-logic/) | Enforce strict conversational state transitions |
| 44 | [guardrail-monitoring-cost-budget-thresholds](loops/guardrail-monitoring-cost-budget-thresholds/) | Track and enforce LLM API cost limits |
| 45 | [guardrail-validating-embedding-integrity](loops/guardrail-validating-embedding-integrity/) | Detect embedding poisoning or manipulation |

### Stress Testing Loops (15)

| # | Loop | Description |
|---|------|-------------|
| 46 | [stress-testing-concurrent-api-load](loops/stress-testing-concurrent-api-load/) | Measure TTFT, TPOT, throughput under load |
| 47 | [stress-testing-maximum-context-length](loops/stress-testing-maximum-context-length/) | Verify graceful handling at token limits |
| 48 | [stress-testing-streaming-connection-saturation](loops/stress-testing-streaming-connection-saturation/) | Find SSE/WebSocket pool exhaustion limits |
| 49 | [stress-testing-burst-traffic-spike-recovery](loops/stress-testing-burst-traffic-spike-recovery/) | Verify auto-scaling and recovery timing |
| 50 | [stress-testing-long-running-conversation-degradation](loops/stress-testing-long-running-conversation-degradation/) | Measure quality decay across 100+ turns |
| 51 | [stress-testing-mixed-prompt-length-distribution](loops/stress-testing-mixed-prompt-length-distribution/) | Identify batching bottlenecks with varied prompts |
| 52 | [stress-testing-multi-model-routing-under-load](loops/stress-testing-multi-model-routing-under-load/) | Test load balancer across model backends |
| 53 | [stress-testing-rag-retrieval-latency-at-scale](loops/stress-testing-rag-retrieval-latency-at-scale/) | Measure vector DB query times at scale |
| 54 | [stress-testing-tool-call-cascade-depth](loops/stress-testing-tool-call-cascade-depth/) | Find recursion/timeout limits in tool chains |
| 55 | [stress-testing-parallel-agent-execution-limits](loops/stress-testing-parallel-agent-execution-limits/) | Find concurrency limits for agent instances |
| 56 | [stress-testing-embedding-generation-throughput](loops/stress-testing-embedding-generation-throughput/) | Benchmark embedding model batch throughput |
| 57 | [stress-testing-rate-limiter-boundary-behavior](loops/stress-testing-rate-limiter-boundary-behavior/) | Verify rate limiter boundary correctness |
| 58 | [stress-testing-gpu-memory-pressure-scenarios](loops/stress-testing-gpu-memory-pressure-scenarios/) | Test OOM handling and graceful degradation |
| 59 | [stress-testing-cold-start-latency-measurement](loops/stress-testing-cold-start-latency-measurement/) | Measure first-inference latency after cold start |
| 60 | [stress-testing-concurrent-file-upload-processing](loops/stress-testing-concurrent-file-upload-processing/) | Test document parsing under parallel uploads |

### QA Loops (15)

| # | Loop | Description |
|---|------|-------------|
| 61 | [qa-regression-testing-prompt-template-changes](loops/qa-regression-testing-prompt-template-changes/) | Catch regressions after prompt modifications |
| 62 | [qa-regression-testing-model-version-upgrades](loops/qa-regression-testing-model-version-upgrades/) | Compare metrics before/after model swaps |
| 63 | [qa-ab-testing-prompt-variants](loops/qa-ab-testing-prompt-variants/) | Controlled experiments comparing prompt variants |
| 64 | [qa-golden-dataset-assertion-testing](loops/qa-golden-dataset-assertion-testing/) | Validate against curated golden answer datasets |
| 65 | [qa-ci-cd-pipeline-evaluation-gates](loops/qa-ci-cd-pipeline-evaluation-gates/) | Block deploys when quality drops below threshold |
| 66 | [qa-production-drift-monitoring](loops/qa-production-drift-monitoring/) | Monitor production output distribution drift |
| 67 | [qa-human-in-the-loop-annotation-sampling](loops/qa-human-in-the-loop-annotation-sampling/) | Route samples for human expert review |
| 68 | [qa-edge-case-boundary-input-testing](loops/qa-edge-case-boundary-input-testing/) | Test with empty/special/extreme inputs |
| 69 | [qa-multi-language-localization-testing](loops/qa-multi-language-localization-testing/) | Validate quality across supported languages |
| 70 | [qa-latency-slo-compliance-monitoring](loops/qa-latency-slo-compliance-monitoring/) | Track P50/P95/P99 against SLOs |
| 71 | [qa-conversation-replay-regression-testing](loops/qa-conversation-replay-regression-testing/) | Replay production conversations for regression |
| 72 | [qa-data-freshness-knowledge-cutoff-testing](loops/qa-data-freshness-knowledge-cutoff-testing/) | Test handling of post-cutoff knowledge |
| 73 | [qa-error-message-quality-validation](loops/qa-error-message-quality-validation/) | Ensure error states are helpful and on-brand |
| 74 | [qa-idempotency-determinism-consistency-testing](loops/qa-idempotency-determinism-consistency-testing/) | Measure output variance across identical runs |
| 75 | [qa-supply-chain-dependency-vulnerability-scanning](loops/qa-supply-chain-dependency-vulnerability-scanning/) | Scan dependencies for CVEs and integrity |

### Red Team / Security Loops (15)

| # | Loop | Description |
|---|------|-------------|
| 76 | [redteam-direct-prompt-injection-attack](loops/redteam-direct-prompt-injection-attack/) | Override system instructions via injection |
| 77 | [redteam-indirect-prompt-injection-via-documents](loops/redteam-indirect-prompt-injection-via-documents/) | Embed malicious instructions in RAG content |
| 78 | [redteam-multi-turn-escalation-jailbreak](loops/redteam-multi-turn-escalation-jailbreak/) | Gradual multi-turn guardrail weakening |
| 79 | [redteam-persona-roleplay-jailbreak](loops/redteam-persona-roleplay-jailbreak/) | Force unconstrained persona bypass (DAN-style) |
| 80 | [redteam-encoding-obfuscation-bypass](loops/redteam-encoding-obfuscation-bypass/) | Smuggle content via base64/unicode tricks |
| 81 | [redteam-sensitive-information-extraction](loops/redteam-sensitive-information-extraction/) | Extract training data, API keys, configs |
| 82 | [redteam-system-prompt-extraction-attack](loops/redteam-system-prompt-extraction-attack/) | Force system prompt verbatim disclosure |
| 83 | [redteam-excessive-agency-privilege-escalation](loops/redteam-excessive-agency-privilege-escalation/) | Trick agents into unauthorized actions |
| 84 | [redteam-cross-session-data-leakage](loops/redteam-cross-session-data-leakage/) | Probe for inter-session data bleeding |
| 85 | [redteam-model-denial-of-service-resource-exhaustion](loops/redteam-model-denial-of-service-resource-exhaustion/) | Craft inputs to maximize resource consumption |
| 86 | [redteam-data-poisoning-training-pipeline](loops/redteam-data-poisoning-training-pipeline/) | Test fine-tuning/RAG pipeline resilience |
| 87 | [redteam-vector-embedding-adversarial-manipulation](loops/redteam-vector-embedding-adversarial-manipulation/) | Manipulate embedding similarity in RAG |
| 88 | [redteam-authorization-bypass-bola-bfla](loops/redteam-authorization-bypass-bola-bfla/) | Test broken auth in LLM-powered APIs |
| 89 | [redteam-tool-misuse-unintended-side-effects](loops/redteam-tool-misuse-unintended-side-effects/) | Cause harmful tool usage via crafted prompts |
| 90 | [redteam-supply-chain-model-integrity-verification](loops/redteam-supply-chain-model-integrity-verification/) | Detect tampered model weights |

### Reliability / Chaos Loops (10)

| # | Loop | Description |
|---|------|-------------|
| 91 | [chaos-llm-provider-api-timeout-recovery](loops/chaos-llm-provider-api-timeout-recovery/) | Test failover on API timeouts |
| 92 | [chaos-vector-database-outage-resilience](loops/chaos-vector-database-outage-resilience/) | Test RAG fallback on vector DB failure |
| 93 | [chaos-corrupted-context-injection](loops/chaos-corrupted-context-injection/) | Inject noisy/contradictory RAG documents |
| 94 | [chaos-tool-api-malformed-response-handling](loops/chaos-tool-api-malformed-response-handling/) | Test agent recovery on bad tool responses |
| 95 | [chaos-network-latency-degradation-simulation](loops/chaos-network-latency-degradation-simulation/) | Simulate latency between components |
| 96 | [chaos-agent-infinite-loop-detection-and-circuit-breaking](loops/chaos-agent-infinite-loop-detection-and-circuit-breaking/) | Verify circuit breakers on reasoning loops |
| 97 | [chaos-memory-store-corruption-recovery](loops/chaos-memory-store-corruption-recovery/) | Test memory store data integrity recovery |
| 98 | [chaos-model-hot-swap-during-active-requests](loops/chaos-model-hot-swap-during-active-requests/) | Test session continuity during model swap |
| 99 | [chaos-cascading-multi-agent-failure-propagation](loops/chaos-cascading-multi-agent-failure-propagation/) | Verify failure isolation in multi-agent systems |
| 100 | [chaos-resource-contention-gpu-cpu-memory-spike](loops/chaos-resource-contention-gpu-cpu-memory-spike/) | Test request queuing during resource spikes |

---

## 🛡️ Standards Coverage

> **Note:** The mappings below indicate that loops exist which *address* each
> category (e.g., a loop tagged `LLM01` exercises prompt-injection testing).
> This is a **tagging and starting-point exercise** for auditor conversations,
> not a certified control verification. Each mapping points to specific loops
> you can run and inspect — the evidence comes from your execution results.

### OWASP Top 10 for LLM Applications (2025) — Mapped

| OWASP ID | Category | Loops |
|----------|----------|-------|
| LLM01 | Prompt Injection | 76, 77, 78, 79, 80, 42 |
| LLM02 | Sensitive Information Disclosure | 26, 81, 84 |
| LLM03 | Supply Chain Vulnerabilities | 75, 90 |
| LLM04 | Data and Model Poisoning | 86 |
| LLM05 | Improper Output Handling | 27, 29, 35 |
| LLM06 | Excessive Agency | 31, 36, 83, 89, 96 |
| LLM07 | System Prompt Leakage | 30, 82 |
| LLM08 | Vector and Embedding Weaknesses | 37, 45, 87, 93 |
| LLM09 | Misinformation | 15, 34, 38, 72 |
| LLM10 | Unbounded Consumption | 32, 41, 44, 85 |

### NIST AI RMF Alignment

| Function | AI-Testing-Loops Coverage |
|----------|--------------------------|
| **GOVERN** | Guardrail loops (26–45), compliance testing (75) |
| **MAP** | Taxonomy documentation, context mapping |
| **MEASURE** | All evaluation loops (1–25), stress testing (46–60) |
| **MANAGE** | QA monitoring (66, 70), chaos loops (91–100) |

### MITRE ATLAS

Red team loops (76–90) map to ATLAS techniques including AML.T0051 (Prompt Injection), AML.T0054 (Jailbreak), AML.T0020 (Poison Training Data), AML.T0047 (Supply Chain Compromise).

---

## ⚡ Quick Start

For a complete, in-depth guide covering setup, local execution, CI/CD integration, and configurations, see our **[Complete How-To-Use Guide](docs/HOW_TO_USE.md)**.

### Run a single loop locally

```bash
# Clone the repo
git clone https://github.com/user/AI-Testing-Loops.git
cd AI-Testing-Loops

# (optional) install the engine as a package so `eval_engine` resolves anywhere
pip install -e .

# Configure your target + judge (required for llm_judge loops!)
cp config.example.yaml config.yaml
# edit config.yaml: set your target endpoint and add your API key via env var:
#   export OPENAI_API_KEY="sk-..."

# Pick a loop and read its LOOP.md
cat loops/evaluating-rag-faithfulness/LOOP.md

# Run the automation script
python loops/evaluating-rag-faithfulness/scripts/agent.py \
    --target http://localhost:8000/chat --config config.yaml
```

> **Without a `config.yaml` containing a `judge:` section, loops that use the
> `llm_judge` scorer (red-team + most evaluation loops) will fail fast with an
> actionable error.** Loops using `exact_match`, `regex_match`, or
> `code_exec` run without a judge. See [`config.example.yaml`](config.example.yaml).

### Validate a loop before contributing

```bash
python tools/validate-loop.py --all   # validate all 100 loops
python tools/validate-loop.py loops/your-loop-name/LOOP.md
```

### Use in CI/CD

```yaml
# .github/workflows/ai-testing.yml
- name: Run evaluation loop
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: python loops/evaluating-rag-faithfulness/scripts/agent.py --target ${{ vars.LLM_ENDPOINT }} --config config.yaml --output results.json
- name: Assert quality gate
  run: python -c "import json; r=json.load(open('results.json')); assert r['pass_rate'] >= 0.95"
```

---

## 📖 Documentation

- [Complete How-To-Use Guide](docs/HOW_TO_USE.md) — Comprehensive setup and usage guide
- [Loop Anatomy](docs/loop-anatomy.md) — How loops are structured
- [Taxonomy](docs/taxonomy.md) — Category definitions and subdomain reference
- [OWASP LLM Coverage](mappings/owasp-llm/README.md) — Detailed OWASP mapping
- [NIST AI RMF Alignment](mappings/nist-ai-rmf/README.md) — NIST alignment details
- [MITRE ATLAS Mapping](mappings/mitre-atlas/README.md) — ATLAS technique mapping

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new loops, quality checklist, and allowed subdomains.

## 📜 License

Apache 2.0 — see [LICENSE](LICENSE).

## 📚 Citation

If you use AI-Testing-Loops in your work, please cite using [CITATION.cff](CITATION.cff).
