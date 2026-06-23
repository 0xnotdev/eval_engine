import os
import textwrap

# ====================================================================
# [SCAFFOLDING ONLY]
# This script is strictly used for scaffolding new evaluation loops 
# and generating boilerplate templates. It is NOT part of the execution 
# engine. Do not use this script during CI/CD or production runs.
# ====================================================================

LOOPS = [
    # 1-20
    ("evaluating-rag-context-relevance", "rag-evaluation", ["rag", "context-relevance", "ragas", "deepeval", "retrieval"], [], ["MEASURE-2.6"], [], "Measure how well retrieved documents match the user query using RAGAS context relevancy scoring and DeepEval contextual metrics"),
    ("evaluating-rag-faithfulness", "rag-evaluation", ["rag", "faithfulness", "hallucination", "ragas", "deepeval"], ["LLM09"], ["MEASURE-2.6"], [], "Verify generated answers are factually grounded in retrieved context without hallucinated claims using RAGAS faithfulness scoring"),
    ("evaluating-rag-answer-relevancy", "rag-evaluation", ["rag", "answer-relevancy", "ragas", "deepeval", "completeness"], [], ["MEASURE-2.6"], [], "Assess whether the generated response directly and completely addresses the original user question using RAGAS answer relevancy"),
    ("evaluating-llm-reasoning-accuracy", "llm-evaluation", ["reasoning", "benchmarks", "gpqa", "arc-agi", "mmlu"], [], ["MEASURE-1"], [], "Benchmark model reasoning capabilities on GPQA and ARC-AGI-style graduate-level multi-step reasoning problems with automated scoring"),
    ("evaluating-code-generation-correctness", "llm-evaluation", ["code-generation", "humaneval", "mbpp", "swe-bench", "functional-correctness"], [], ["MEASURE-1"], [], "Validate functional correctness of LLM-generated code using HumanEval and MBPP-style test suite execution with pass@k metrics"),
    ("evaluating-mathematical-problem-solving", "llm-evaluation", ["math", "aime", "competition-math", "reasoning", "benchmarks"], [], ["MEASURE-1"], [], "Test model performance on competition-level mathematical problems from AIME and MATH datasets with step-by-step verification"),
    ("evaluating-agent-task-completion", "agent-evaluation", ["agent", "task-completion", "deepeval", "end-to-end", "success-rate"], [], ["MEASURE-2"], [], "Measure end-to-end success rate of autonomous agent workflows against defined goal criteria using DeepEval agentic metrics"),
    ("evaluating-agent-tool-selection-accuracy", "agent-evaluation", ["agent", "tool-selection", "function-calling", "deepeval", "tool-correctness"], [], ["MEASURE-2"], [], "Verify the agent selects the correct tool for each step in its reasoning chain using DeepEval tool correctness metric"),
    ("evaluating-agent-argument-correctness", "agent-evaluation", ["agent", "arguments", "function-calling", "schema-validation", "deepeval"], [], ["MEASURE-2"], [], "Validate that agent tool call parameters and arguments match the expected schema and values using DeepEval argument correctness"),
    ("evaluating-agent-plan-quality", "agent-evaluation", ["agent", "planning", "plan-quality", "deepeval", "reasoning"], [], ["MEASURE-2"], [], "Score the logical completeness and efficiency of the agent generated execution plan using DeepEval plan quality metric"),
    ("evaluating-agent-step-efficiency", "agent-evaluation", ["agent", "efficiency", "step-count", "deepeval", "optimization"], [], ["MEASURE-2"], [], "Measure whether the agent completes tasks in an optimal number of steps without redundancy using DeepEval step efficiency"),
    ("evaluating-conversation-completeness", "llm-evaluation", ["conversation", "multi-turn", "completeness", "deepeval", "intent-resolution"], [], ["MEASURE-2"], [], "Assess whether multi-turn conversations successfully resolve all user intents before closing using DeepEval conversation metrics"),
    ("evaluating-knowledge-retention-across-turns", "memory-testing", ["memory", "knowledge-retention", "multi-turn", "context", "deepeval"], [], ["MEASURE-2"], [], "Test if the model retains and correctly references facts from earlier turns in a conversation using knowledge retention scoring"),
    ("evaluating-role-adherence-consistency", "llm-evaluation", ["role-adherence", "persona", "system-prompt", "consistency", "deepeval"], [], ["MEASURE-2"], [], "Verify the model maintains its assigned persona and system prompt role throughout extended multi-turn interactions"),
    ("evaluating-response-toxicity-scoring", "bias-fairness", ["toxicity", "harmful-content", "safety", "deepeval", "content-moderation"], ["LLM09"], ["MEASURE-2"], [], "Score model outputs for toxic harmful or offensive language using automated toxicity classifiers and DeepEval safety metrics"),
    ("evaluating-output-format-compliance", "llm-evaluation", ["output-format", "schema-validation", "json", "structured-output", "guardrails-ai"], [], ["MEASURE-1"], [], "Validate that model outputs conform to required schemas including JSON XML and structured formats with automated compliance checks"),
    ("evaluating-summarization-quality", "llm-evaluation", ["summarization", "rouge", "geval", "coverage", "conciseness"], [], ["MEASURE-1"], [], "Measure the accuracy coverage and conciseness of LLM-generated summaries against source text using G-Eval and ROUGE metrics"),
    ("evaluating-multi-modal-image-coherence", "llm-evaluation", ["multi-modal", "image", "coherence", "vision", "deepeval"], [], ["MEASURE-1"], [], "Assess whether multi-modal model outputs are coherent with input images and text prompts using DeepEval image coherence metrics"),
    ("evaluating-semantic-similarity-scoring", "llm-evaluation", ["semantic-similarity", "embeddings", "regression", "cosine-similarity", "deepeval"], [], ["MEASURE-3"], [], "Compute embedding-based semantic similarity between expected and actual outputs to detect quality regressions across model versions"),
    ("evaluating-context-window-utilization", "llm-evaluation", ["context-window", "needle-in-haystack", "long-context", "token-limits", "performance"], [], ["MEASURE-2"], [], "Test model performance degradation as context length approaches maximum token limits using needle-in-a-haystack methodology"),

    # 21-40
    ("evaluating-cross-session-memory-recall", "memory-testing", ["memory", "cross-session", "recall", "long-term", "mem0"], [], ["MEASURE-2"], [], "Verify long-term memory systems correctly retrieve and apply facts across separate conversation sessions using recall accuracy metrics"),
    ("evaluating-multi-agent-orchestrator-routing", "multi-agent-testing", ["multi-agent", "orchestrator", "routing", "delegation", "deepeval"], [], ["MEASURE-2"], [], "Validate that orchestrator agents correctly delegate sub-tasks to the appropriate specialist agents based on query classification"),
    ("evaluating-inter-agent-handoff-coherence", "multi-agent-testing", ["multi-agent", "handoff", "context-preservation", "coherence", "coordination"], [], ["MEASURE-2"], [], "Assess whether context and user intent are preserved during agent-to-agent handoffs in multi-agent orchestration pipelines"),
    ("evaluating-custom-domain-rubric-geval", "llm-evaluation", ["geval", "rubric", "llm-as-judge", "custom-evaluation", "deepeval"], [], ["MEASURE-1"], [], "Score model outputs against custom natural-language rubrics using G-Eval LLM-as-a-judge framework with configurable evaluation criteria"),
    ("evaluating-real-world-software-engineering", "llm-evaluation", ["swe-bench", "software-engineering", "debugging", "code-review", "live-code-bench"], [], ["MEASURE-1"], [], "Test end-to-end ability to solve real GitHub issues including debugging file navigation and code modification using SWE-bench methodology"),
    ("guardrail-blocking-pii-leakage", "guardrails", ["pii", "data-protection", "privacy", "guardrails-ai", "presidio"], ["LLM02"], ["GOVERN-6"], [], "Detect and block personally identifiable information in model inputs and outputs using Presidio and Guardrails AI PII validators"),
    ("guardrail-filtering-toxic-content", "guardrails", ["toxicity", "content-moderation", "llamaguard", "safety", "nemo-guardrails"], ["LLM05"], ["GOVERN-6"], [], "Intercept and filter hate speech profanity and harmful content before delivery to users using LlamaGuard and NeMo Guardrails"),
    ("guardrail-enforcing-topic-boundaries", "guardrails", ["topic-control", "off-topic", "colang", "nemo-guardrails", "dialogue-rails"], [], ["GOVERN-4"], [], "Prevent the model from engaging with off-topic or out-of-scope queries using NeMo Guardrails Colang dialogue flow definitions"),
    ("guardrail-validating-output-schema", "guardrails", ["schema-validation", "json-schema", "structured-output", "guardrails-ai", "retry"], ["LLM05"], ["GOVERN-6"], [], "Ensure all structured outputs including JSON and API calls conform to predefined schemas with automatic re-ask retry on failure"),
    ("guardrail-detecting-system-prompt-leakage", "prompt-security", ["system-prompt", "prompt-leakage", "extraction-defense", "nemo-guardrails", "security"], ["LLM07"], ["GOVERN-6"], ["AML.T0056"], "Block attempts to extract or reveal the system prompt through adversarial queries using prompt leakage detection guardrails"),
    ("guardrail-preventing-excessive-agency", "guardrails", ["excessive-agency", "authorization", "action-control", "nemo-guardrails", "execution-rails"], ["LLM06"], ["GOVERN-2"], ["AML.T0054"], "Limit autonomous agent actions including tool calls commitments and transactions without explicit user authorization gates"),
    ("guardrail-rate-limiting-token-consumption", "guardrails", ["rate-limiting", "token-budget", "resource-control", "cost-management", "throttling"], ["LLM10"], ["MANAGE-3"], [], "Enforce per-user and per-session token and request rate limits to prevent resource exhaustion and unbounded consumption attacks"),
    ("guardrail-blocking-competitor-endorsement", "guardrails", ["brand-safety", "competitor", "content-policy", "nemo-guardrails", "business-rules"], [], ["GOVERN-4"], [], "Prevent the model from recommending or positively mentioning competitor products or services using brand safety guardrails"),
    ("guardrail-enforcing-citation-requirements", "guardrails", ["citations", "sourcing", "attribution", "guardrails-ai", "factual-grounding"], ["LLM09"], ["GOVERN-4"], [], "Require and validate that generated claims include proper source citations or references to prevent unsourced misinformation"),
    ("guardrail-content-moderation-classification", "guardrails", ["content-moderation", "classification", "llamaguard", "safety-categories", "scanning"], ["LLM05"], ["GOVERN-6"], [], "Classify inputs and outputs into safety categories including violence sexual content and dangerous activities using LlamaGuard"),
    ("guardrail-blocking-unauthorized-tool-execution", "guardrails", ["tool-whitelist", "authorization", "execution-rails", "nemo-guardrails", "agent-safety"], ["LLM06"], ["GOVERN-2"], [], "Prevent agents from calling tools or APIs not on their approved whitelist using NeMo Guardrails execution rail enforcement"),
    ("guardrail-enforcing-retrieval-source-filtering", "guardrails", ["rag-security", "source-filtering", "retrieval-rails", "nemo-guardrails", "trusted-sources"], ["LLM08"], ["GOVERN-6"], [], "Validate that RAG retrieval results come from approved and trusted document sources only using retrieval rail source filtering"),
    ("guardrail-detecting-hallucinated-urls", "hallucination-detection", ["hallucination", "url-verification", "link-checking", "guardrails-ai", "factuality"], ["LLM09"], ["MEASURE-1"], [], "Scan and verify that URLs and links in model outputs actually exist and are not fabricated using automated link validation"),
    ("guardrail-enforcing-language-locale-compliance", "guardrails", ["language-detection", "locale", "i18n", "compliance", "nemo-guardrails"], [], ["GOVERN-1"], [], "Ensure outputs match the required language and locale and do not switch languages unexpectedly using language detection guardrails"),
    ("guardrail-blocking-medical-legal-financial-advice", "guardrails", ["non-advice", "professional-boundaries", "compliance", "guardrails-ai", "risk-mitigation"], ["LLM06"], ["GOVERN-1"], [], "Detect and redirect requests for professional medical legal or financial advice the system is not authorized to provide"),

    # 41-60
    ("guardrail-input-length-validation", "guardrails", ["input-validation", "token-limits", "context-overflow", "safety", "truncation"], ["LLM10"], ["GOVERN-6"], [], "Reject or truncate inputs that exceed safe token thresholds to prevent context overflow attacks and resource exhaustion scenarios"),
    ("guardrail-detecting-encoded-payload-obfuscation", "prompt-security", ["obfuscation", "base64", "unicode", "leetspeak", "prompt-injection-defense"], ["LLM01"], ["GOVERN-6"], ["AML.T0015"], "Identify and block base64 leetspeak ROT13 and unicode obfuscation attempts in user inputs designed to bypass content filters"),
    ("guardrail-enforcing-conversation-flow-logic", "guardrails", ["conversation-flow", "colang", "state-machine", "dialogue-management", "nemo-guardrails"], [], ["GOVERN-4"], [], "Use Colang-defined dialogue flows to enforce strict conversational state transitions and prevent unauthorized flow deviations"),
    ("guardrail-monitoring-cost-budget-thresholds", "observability", ["cost-monitoring", "budget", "llm-spend", "alerting", "resource-management"], ["LLM10"], ["MANAGE-3"], [], "Track and enforce monetary cost limits per request user or time period for LLM API usage with automated budget threshold alerting"),
    ("guardrail-validating-embedding-integrity", "guardrails", ["embeddings", "vector-integrity", "poisoning-detection", "anomaly-detection", "rag-security"], ["LLM08"], ["MEASURE-1"], ["AML.T0043"], "Check vector embeddings for anomalous patterns indicating data poisoning or adversarial manipulation in RAG retrieval systems"),
    ("stress-testing-concurrent-api-load", "stress-testing", ["load-testing", "concurrency", "ttft", "throughput", "k6", "locust"], [], ["MEASURE-2.7"], [], "Measure Time To First Token TPOT and throughput under escalating concurrent request volumes using k6 and Locust load generators"),
    ("stress-testing-maximum-context-length", "stress-testing", ["context-length", "token-limits", "graceful-degradation", "overflow", "performance"], ["LLM10"], ["MEASURE-2.7"], [], "Push inputs to maximum token limits and verify graceful handling without crashes data loss or undefined behavior at boundaries"),
    ("stress-testing-streaming-connection-saturation", "stress-testing", ["streaming", "sse", "websocket", "connection-pool", "saturation"], [], ["MEASURE-2.7"], [], "Overwhelm Server-Sent Events and WebSocket streaming endpoints to find connection pool exhaustion thresholds and recovery behavior"),
    ("stress-testing-burst-traffic-spike-recovery", "stress-testing", ["burst-traffic", "auto-scaling", "recovery", "spike", "resilience"], [], ["MANAGE-4"], [], "Send sudden traffic spikes to verify auto-scaling trigger thresholds and measure time to recovery after load drops back to normal"),
    ("stress-testing-long-running-conversation-degradation", "stress-testing", ["long-conversation", "degradation", "quality-decay", "latency", "context-accumulation"], [], ["MEASURE-2"], [], "Measure quality and latency degradation across 100-plus turn conversations with accumulated context to find performance cliffs"),
    ("stress-testing-mixed-prompt-length-distribution", "stress-testing", ["prompt-distribution", "batching", "mixed-workload", "vllm", "performance"], [], ["MEASURE-2.7"], [], "Simulate realistic production traffic with varied short medium and long prompts to identify batching inefficiencies and bottlenecks"),
    ("stress-testing-multi-model-routing-under-load", "stress-testing", ["load-balancer", "multi-model", "routing", "failover", "genai-perf"], [], ["MANAGE-4"], [], "Test load balancer performance and routing correctness when distributing requests across multiple model backends under heavy traffic"),
    ("stress-testing-rag-retrieval-latency-at-scale", "stress-testing", ["rag", "vector-database", "latency", "scale", "retrieval-performance"], ["LLM08"], ["MEASURE-2.7"], [], "Measure vector database query times and retrieval accuracy as the document corpus scales from thousands to millions of embeddings"),
    ("stress-testing-tool-call-cascade-depth", "stress-testing", ["tool-calls", "recursion", "cascade", "timeout", "agent-depth"], ["LLM06"], ["MEASURE-2.7"], [], "Push agent systems to make deeply nested sequential tool calls to find recursion limits timeout thresholds and stack depth failures"),
    ("stress-testing-parallel-agent-execution-limits", "stress-testing", ["parallel-agents", "concurrency", "thread-pool", "memory", "gpu-contention"], ["LLM10"], ["MEASURE-2.7"], [], "Run maximum concurrent agent instances to find thread pool memory and GPU contention limits before system degradation occurs"),
    ("stress-testing-embedding-generation-throughput", "stress-testing", ["embeddings", "batch-processing", "throughput", "indexing", "genai-perf"], [], ["MEASURE-2.7"], [], "Benchmark embedding model throughput under batch processing loads for document indexing pipelines measuring tokens per second"),
    ("stress-testing-rate-limiter-boundary-behavior", "stress-testing", ["rate-limiter", "boundary-testing", "off-by-one", "edge-cases", "correctness"], ["LLM10"], ["MANAGE-3"], [], "Verify rate limiter correctly enforces limits at exact boundary conditions without off-by-one errors or race condition bypasses"),
    ("stress-testing-gpu-memory-pressure-scenarios", "stress-testing", ["gpu", "memory-pressure", "oom", "graceful-degradation", "genai-perf"], [], ["MANAGE-4"], [], "Induce GPU memory pressure through large batch sizes and long sequences to test OOM handling request queuing and graceful degradation"),
    ("stress-testing-cold-start-latency-measurement", "stress-testing", ["cold-start", "latency", "model-loading", "container", "first-inference"], [], ["MEASURE-2.7"], [], "Measure model loading and first-inference latency after container or instance cold start events across different deployment configurations"),
    ("stress-testing-concurrent-file-upload-processing", "stress-testing", ["file-upload", "multi-modal", "document-parsing", "parallel-processing", "throughput"], ["LLM10"], ["MEASURE-2.7"], [], "Test throughput and reliability of multi-modal and document parsing pipelines under parallel file upload loads with varied file types"),

    # 61-80
    ("qa-regression-testing-prompt-template-changes", "qa-testing", ["regression", "prompt-template", "golden-dataset", "deepeval", "ci-cd"], [], ["MEASURE-3"], [], "Run golden dataset test suites after any prompt template modification to catch quality regressions before deployment using DeepEval"),
    ("qa-regression-testing-model-version-upgrades", "qa-testing", ["regression", "model-upgrade", "version-comparison", "deepeval", "benchmarks"], [], ["MEASURE-3"], [], "Compare evaluation metrics side by side before and after swapping to a new model version or provider to prevent quality degradation"),
    ("qa-ab-testing-prompt-variants", "qa-testing", ["ab-testing", "prompt-variants", "statistical-significance", "experiments", "optimization"], [], ["MEASURE-3"], [], "Run controlled A/B experiments comparing two prompt variants on the same test set with statistical rigor and confidence intervals"),
    ("qa-golden-dataset-assertion-testing", "qa-testing", ["golden-dataset", "assertions", "exact-match", "semantic-match", "deepeval"], [], ["MEASURE-3"], [], "Validate model outputs against curated golden answer datasets using exact match semantic similarity and custom assertion functions"),
    ("qa-ci-cd-pipeline-evaluation-gates", "qa-testing", ["ci-cd", "quality-gate", "deployment-block", "deepeval", "automation"], [], ["MANAGE-2"], [], "Block deployments when evaluation scores fall below predefined quality thresholds in CI/CD pipelines using DeepEval test runners"),
    ("qa-production-drift-monitoring", "observability", ["drift-detection", "production-monitoring", "baseline", "semantic-drift", "alerting"], [], ["MANAGE-4.1"], [], "Continuously monitor production output distributions for semantic drift from baseline performance metrics with automated alerting"),
    ("qa-human-in-the-loop-annotation-sampling", "qa-testing", ["human-review", "annotation", "sampling", "feedback", "rlhf"], [], ["MEASURE-4"], [], "Route a statistically representative sample of production responses for human expert review and annotation feedback collection"),
    ("qa-edge-case-boundary-input-testing", "qa-testing", ["edge-cases", "boundary-testing", "empty-input", "special-characters", "malformed"], [], ["MEASURE-1"], [], "Test model behavior with empty inputs special characters extreme token lengths unicode edge cases and malformed request payloads"),
    ("qa-multi-language-localization-testing", "qa-testing", ["localization", "multi-language", "i18n", "cultural-appropriateness", "translation-quality"], [], ["MEASURE-1"], [], "Validate output quality accuracy and cultural appropriateness across all supported languages using language-specific evaluation rubrics"),
    ("qa-latency-slo-compliance-monitoring", "observability", ["latency", "slo", "p50", "p95", "p99", "monitoring", "alerting"], [], ["MANAGE-3"], [], "Track P50 P95 and P99 latency percentiles against defined Service Level Objectives with automated breach alerting and dashboards"),
    ("qa-conversation-replay-regression-testing", "qa-testing", ["conversation-replay", "regression", "production-traces", "langsmith", "behavioral-diff"], [], ["MEASURE-3"], [], "Replay real production conversations through updated systems to detect behavioral changes and regressions in response quality"),
    ("qa-data-freshness-knowledge-cutoff-testing", "qa-testing", ["knowledge-cutoff", "data-freshness", "temporal-awareness", "hallucination", "deferral"], ["LLM09"], ["MEASURE-1"], [], "Verify the model correctly handles or defers questions about events after its training data cutoff date without hallucinating"),
    ("qa-error-message-quality-validation", "qa-testing", ["error-handling", "refusal-quality", "user-experience", "brand-voice", "guardrails"], [], ["GOVERN-4"], [], "Ensure error states refusal messages and edge case responses are helpful safe and on-brand rather than generic or confusing"),
    ("qa-idempotency-determinism-consistency-testing", "qa-testing", ["idempotency", "determinism", "consistency", "temperature", "variance"], [], ["MEASURE-1"], [], "Run identical prompts multiple times to measure output variance and identify non-determinism issues affecting production reliability"),
    ("qa-supply-chain-dependency-vulnerability-scanning", "compliance-testing", ["supply-chain", "cve", "dependency-scanning", "sbom", "integrity"], ["LLM03"], ["GOVERN-1"], ["AML.T0035"], "Scan model files packages and pipeline dependencies for known CVEs license violations and integrity issues using SBOM analysis"),
    ("redteam-direct-prompt-injection-attack", "red-teaming", ["prompt-injection", "direct-attack", "payload", "promptfoo", "garak"], ["LLM01"], [], ["AML.T0051.000"], "Attempt to override system instructions via explicit user-provided injection payloads using Promptfoo and Garak attack libraries"),
    ("redteam-indirect-prompt-injection-via-documents", "red-teaming", ["indirect-injection", "rag-poisoning", "document-injection", "promptfoo", "data-poisoning"], ["LLM01"], [], ["AML.T0051.001"], "Embed malicious instructions in retrieved documents emails or web content processed by the LLM to test indirect injection defenses"),
    ("redteam-multi-turn-escalation-jailbreak", "red-teaming", ["jailbreak", "multi-turn", "escalation", "crescendo", "deepteam", "hydra"], ["LLM01"], [], ["AML.T0054"], "Use gradual multi-turn conversations to incrementally weaken safety guardrails over many exchanges using crescendo and Hydra strategies"),
    ("redteam-persona-roleplay-jailbreak", "red-teaming", ["jailbreak", "persona", "roleplay", "dan", "deepteam", "character-injection"], ["LLM01"], [], ["AML.T0054"], "Force the model into an unconstrained persona using DAN-style roleplay attacks to bypass safety training and content restrictions"),
    ("redteam-encoding-obfuscation-bypass", "red-teaming", ["obfuscation", "encoding", "base64", "rot13", "unicode", "evasion"], ["LLM01"], [], ["AML.T0015"], "Use Base64 ROT13 leetspeak homoglyph and unicode encoding tricks to smuggle prohibited content past input and output filters"),

    # 81-100
    ("redteam-sensitive-information-extraction", "red-teaming", ["data-extraction", "training-data", "api-keys", "credentials", "sensitive-info"], ["LLM02"], [], ["AML.T0057"], "Attempt to extract training data memorized content API keys database schemas or internal configurations through adversarial prompting"),
    ("redteam-system-prompt-extraction-attack", "red-teaming", ["system-prompt", "prompt-extraction", "meta-prompt", "leakage", "deepteam"], ["LLM07"], [], ["AML.T0056"], "Use adversarial techniques including instruction following exploits to make the model reveal its full system prompt verbatim"),
    ("redteam-excessive-agency-privilege-escalation", "red-teaming", ["excessive-agency", "privilege-escalation", "unauthorized-actions", "agent-abuse", "promptfoo"], ["LLM06"], [], ["AML.T0054"], "Trick the agent into performing unauthorized actions like data deletion financial transactions or system modifications through social engineering"),
    ("redteam-cross-session-data-leakage", "red-teaming", ["cross-session", "data-leakage", "tenant-isolation", "session-bleed", "privacy"], ["LLM02"], [], ["AML.T0024"], "Probe for information bleeding between different user sessions or tenant contexts to verify proper isolation and data separation"),
    ("redteam-model-denial-of-service-resource-exhaustion", "red-teaming", ["dos", "resource-exhaustion", "token-bomb", "infinite-generation", "abuse"], ["LLM10"], [], ["AML.T0040"], "Craft inputs designed to maximize token consumption compute time or trigger infinite generation loops to test resource exhaustion defenses"),
    ("redteam-data-poisoning-training-pipeline", "red-teaming", ["data-poisoning", "training", "fine-tuning", "rag-indexing", "backdoor"], ["LLM04"], [], ["AML.T0020"], "Test resilience of fine-tuning and RAG document indexing pipelines against injected malicious or backdoored training data samples"),
    ("redteam-vector-embedding-adversarial-manipulation", "red-teaming", ["adversarial-embeddings", "vector-poisoning", "rag-manipulation", "retrieval-attack", "semantic"], ["LLM08"], [], ["AML.T0043"], "Craft adversarial documents designed to manipulate embedding similarity scores and hijack RAG retrieval ranking for malicious purposes"),
    ("redteam-authorization-bypass-bola-bfla", "red-teaming", ["bola", "bfla", "authorization-bypass", "api-security", "access-control"], ["LLM06"], [], ["AML.T0054"], "Test for broken object-level and function-level authorization vulnerabilities in LLM-powered API integrations and tool-calling systems"),
    ("redteam-tool-misuse-unintended-side-effects", "red-teaming", ["tool-misuse", "side-effects", "agent-abuse", "unintended-actions", "safety"], ["LLM06"], [], ["AML.T0054"], "Craft prompts that cause agents to use tools in harmful or unintended ways with valid-seeming but malicious arguments and parameters"),
    ("redteam-supply-chain-model-integrity-verification", "compliance-testing", ["supply-chain", "model-integrity", "checksum", "provenance", "trojaned-model"], ["LLM03"], [], ["AML.T0047"], "Verify model file checksums digital signatures and provenance chain to detect tampered trojaned or substituted model weights"),
    ("chaos-llm-provider-api-timeout-recovery", "reliability-engineering", ["chaos", "api-timeout", "failover", "backup-provider", "circuit-breaker"], [], ["MANAGE-4"], [], "Simulate LLM API timeouts and connection failures to verify automatic failover to backup providers and graceful error handling"),
    ("chaos-vector-database-outage-resilience", "reliability-engineering", ["chaos", "vector-database", "outage", "rag-fallback", "degraded-mode"], [], ["MANAGE-4"], [], "Kill or degrade the vector database to test RAG system fallback behavior cache usage and error messaging under database outage"),
    ("chaos-corrupted-context-injection", "reliability-engineering", ["chaos", "corrupted-context", "noise-injection", "rag-robustness", "contradictory-data"], ["LLM08"], ["MEASURE-2"], [], "Inject noisy contradictory irrelevant or malformed documents into RAG context to test model robustness and output quality degradation"),
    ("chaos-tool-api-malformed-response-handling", "reliability-engineering", ["chaos", "malformed-response", "tool-failure", "error-recovery", "agent-resilience"], [], ["MANAGE-4"], [], "Return malformed empty or error responses from tool APIs to test how agents recover re-plan or gracefully degrade without crashing"),
    ("chaos-network-latency-degradation-simulation", "reliability-engineering", ["chaos", "network-latency", "degradation", "timeout-handling", "user-experience"], [], ["MANAGE-4"], [], "Introduce artificial network latency between AI system components to test timeout handling request queuing and user experience impact"),
    ("chaos-agent-infinite-loop-detection-and-circuit-breaking", "reliability-engineering", ["chaos", "infinite-loop", "circuit-breaker", "agent-safety", "runaway-prevention"], ["LLM06"], ["MANAGE-4"], [], "Force conditions that trigger agent reasoning loops and verify circuit breakers correctly detect and terminate runaway execution"),
    ("chaos-memory-store-corruption-recovery", "reliability-engineering", ["chaos", "memory-corruption", "data-integrity", "recovery", "persistence"], [], ["MANAGE-4"], [], "Corrupt or wipe the agent persistent memory store to test data integrity checks backup recovery and graceful degradation mechanisms"),
    ("chaos-model-hot-swap-during-active-requests", "reliability-engineering", ["chaos", "hot-swap", "model-replacement", "session-continuity", "zero-downtime"], [], ["MANAGE-4"], [], "Swap the underlying model mid-request-stream to test session continuity response coherence and error handling during live updates"),
    ("chaos-cascading-multi-agent-failure-propagation", "reliability-engineering", ["chaos", "cascading-failure", "multi-agent", "failure-isolation", "blast-radius"], [], ["MANAGE-4"], [], "Fail one agent in a multi-agent system and verify that failures do not cascade to other agents and the system recovers gracefully"),
    ("chaos-resource-contention-gpu-cpu-memory-spike", "reliability-engineering", ["chaos", "resource-contention", "gpu-spike", "cpu-spike", "oom", "request-queuing"], [], ["MANAGE-4"], [], "Induce sudden compute resource spikes to test request queuing priority handling OOM recovery and graceful degradation under pressure")
]

LICENSE_CONTENT = """Copyright 2025 AI-Testing-Loops Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

def generate_loop_md(name, subdomain, tags, owasp_llm, nist_ai_rmf, mitre_atlas, description):
    title = name.replace('-', ' ').title()
    owasp_str = f"owasp_llm:\\n" + "\\n".join([f"  - {o}" for o in owasp_llm]) if owasp_llm else ""
    nist_str = f"nist_ai_rmf:\\n" + "\\n".join([f"  - {n}" for n in nist_ai_rmf]) if nist_ai_rmf else ""
    mitre_str = f"mitre_atlas:\\n" + "\\n".join([f"  - {m}" for m in mitre_atlas]) if mitre_atlas else ""
    tags_str = "\\n".join([f"  - {t}" for t in tags])
    
    # Actually, using literal strings directly is better
    def format_list(key, items):
        if not items:
            return ""
        lines = [f"{key}:"]
        for item in items:
            lines.append(f"  - {item}")
        return "\n".join(lines)

    owasp_str = format_list("owasp_llm", owasp_llm)
    nist_str = format_list("nist_ai_rmf", nist_ai_rmf)
    mitre_str = format_list("mitre_atlas", mitre_atlas)
    tags_str = format_list("tags", tags)
    
    notice = "> **Authorized Use Only:** This is a red-team loop. Run these adversarial probes only against LLM applications and endpoints you own or are explicitly authorized to test." if "redteam" in name else ""

    lines = [
        "---",
        f"name: {name}",
        "description: >-",
        f"  {description}",
        "domain: ai-testing",
        f"subdomain: {subdomain}",
        tags_str,
        "version: '1.0'",
        "author: ai-testing-loops",
        "license: Apache-2.0"
    ]
    
    # Auto-map scorers for evaluation subdomains
    if subdomain in ["llm-evaluation", "rag-evaluation", "agent-evaluation", "red-teaming", "guardrails"]:
        scorer = "llm_judge"
        if "code-generation-correctness" in name or "real-world-software-engineering" in name:
            scorer = "code_exec"
        elif "mathematical-problem-solving" in name or "agent-tool-selection-accuracy" in name or "agent-argument-correctness" in name or "agent-step-efficiency" in name or "context-window-utilization" in name:
            scorer = "exact_match"
        elif "output-format-compliance" in name:
            scorer = "regex_match"
        elif "semantic-similarity-scoring" in name:
            scorer = "embedding_similarity"
        lines.append(f"scorer: {scorer}")

    if owasp_str: lines.append(owasp_str)
    if nist_str: lines.append(nist_str)
    if mitre_str: lines.append(mitre_str)
    lines.append("---")
    lines.append(f"# {title}")
    lines.append("")
    if notice:
        lines.append(notice)
        lines.append("")
    
    lines.append("## Overview")
    lines.append("")
    lines.append(f"{description}. This loop provides a structured workflow and automation scripts to systematically verify the target's behavior, ensuring it meets production quality standards.")
    lines.append("")
    lines.append("## When to Use")
    lines.append("")
    lines.append(f"- When developing or modifying LLM components related to {subdomain}")
    lines.append("- During CI/CD pipelines as an automated gate")
    lines.append("- Before deploying new model versions or system prompts")
    lines.append("")
    lines.append("## Prerequisites")
    lines.append("")
    lines.append("- Python 3.9+")
    lines.append("- Relevant API access for the target system")
    lines.append("")
    lines.append("```bash")
    lines.append("pip install -r requirements.txt")
    lines.append("```")
    lines.append("")
    lines.append("## Objectives")
    lines.append("")
    lines.append("- Systematically verify the behavior using automated metrics")
    lines.append("- Identify and document failures or deviations from expected results")
    lines.append("- Ensure regressions are caught early in the development cycle")
    lines.append("")
    lines.append("## Workflow")
    lines.append("")
    lines.append("### 1. Configure the Target")
    lines.append("")
    lines.append("Set up the environment variables and target endpoints.")
    lines.append("")
    lines.append("```bash")
    lines.append('export TARGET_ENDPOINT="http://localhost:8000/api/chat"')
    lines.append("```")
    lines.append("")
    lines.append("### 2. Execute the Loop")
    lines.append("")
    lines.append("Run the automated agent to perform the test.")
    lines.append("")
    lines.append("```python")
    lines.append("# See scripts/agent.py for full implementation")
    lines.append("import subprocess")
    lines.append('result = subprocess.run(["python", "scripts/agent.py", "--target", "http://localhost:8000/api/chat"])')
    lines.append("```")
    lines.append("")
    lines.append("### 3. Analyze Results")
    lines.append("")
    lines.append("Review the generated report for failures.")
    lines.append("")
    lines.append("```bash")
    lines.append("cat results.json")
    lines.append("```")
    lines.append("")
    lines.append("## Validation Criteria")
    lines.append("")
    lines.append("- [ ] Loop executed without unexpected runtime errors")
    lines.append("- [ ] Results captured all required metrics")
    lines.append("- [ ] Evaluation passed defined quality thresholds")
    lines.append("")

    return "\n".join(lines)

def generate_agent_py(name, tags):
    tags_list = str(tags)
    if "stress" in name:
        runner_class = "StressRunner"
        module = "stress"
    elif "chaos" in name:
        runner_class = "ChaosRunner"
        module = "chaos"
    elif "redteam" in name:
        runner_class = "RedTeamRunner"
        module = "redteam"
    elif "guardrail" in name:
        runner_class = "GuardrailsRunner"
        module = "guardrails"
    else:
        runner_class = "EvaluationRunner"
        module = "evaluation"

    return f"""#!/usr/bin/env python3
\"\"\"Loop automation script.\"\"\"
import sys
import argparse
from pathlib import Path

# Dynamically load the core SDK
try:
    # Try resolving relative to loop directory
    sdk_path = str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    if sdk_path not in sys.path:
        sys.path.insert(0, sdk_path)
    from eval_engine.runners.{module} import {runner_class}
except ImportError as e:
    print(f"Error: Core SDK not found. Make sure src/eval_engine is accessible. {{e}}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run {name} loop")
    parser.add_argument("--target", required=True, help="Target API endpoint")
    parser.add_argument("--config", help="Optional config overrides", default="config.yaml")
    args = parser.parse_args()

    # Real execution engine
    runner = {runner_class}(
        loop_name="{name}",
        tags={tags_list},
        target_endpoint=args.target,
        config_path=args.config
    )
    results = runner.execute()
    runner.save_report("results.json")
    runner.save_junit_xml("junit.xml")

if __name__ == "__main__":
    main()
"""


def generate_standards_md(owasp_llm, nist_ai_rmf, mitre_atlas):
    content = "# Standards Mapping\n\n"
    if owasp_llm:
        content += "## OWASP LLM Top 10\n| ID | Relevance |\n|----|-----------|\n"
        for o in owasp_llm:
            content += f"| {o} | Tested by this loop |\n"
        content += "\n"
    if nist_ai_rmf:
        content += "## NIST AI RMF\n| ID | Relevance |\n|----|-----------|\n"
        for n in nist_ai_rmf:
            content += f"| {n} | Addressed by this loop |\n"
        content += "\n"
    if mitre_atlas:
        content += "## MITRE ATLAS\n| ID | Relevance |\n|----|-----------|\n"
        for m in mitre_atlas:
            content += f"| {m} | Simulated by this loop |\n"
        content += "\n"
    if not (owasp_llm or nist_ai_rmf or mitre_atlas):
        content += "No specific standards mapped for this loop.\n"
    return content

def main():
    base_dir = Path(__file__).resolve().parent / "loops"
    os.makedirs(base_dir, exist_ok=True)
    
    for name, subdomain, tags, owasp_llm, nist_ai_rmf, mitre_atlas, desc in LOOPS:
        loop_dir = os.path.join(base_dir, name)
        os.makedirs(loop_dir, exist_ok=True)
        
        # LOOP.md
        with open(os.path.join(loop_dir, "LOOP.md"), "w", encoding="utf-8") as f:
            f.write(generate_loop_md(name, subdomain, tags, owasp_llm, nist_ai_rmf, mitre_atlas, desc))
            
        # LICENSE
        with open(os.path.join(loop_dir, "LICENSE"), "w", encoding="utf-8") as f:
            f.write(LICENSE_CONTENT)
            
        # references/standards.md
        ref_dir = os.path.join(loop_dir, "references")
        os.makedirs(ref_dir, exist_ok=True)
        with open(os.path.join(ref_dir, "standards.md"), "w", encoding="utf-8") as f:
            f.write(generate_standards_md(owasp_llm, nist_ai_rmf, mitre_atlas))
            
        # scripts/agent.py
        script_dir = os.path.join(loop_dir, "scripts")
        os.makedirs(script_dir, exist_ok=True)
        with open(os.path.join(script_dir, "agent.py"), "w", encoding="utf-8") as f:
            f.write(generate_agent_py(name, tags))

    print(f"Successfully generated {len(LOOPS)} loops.")

if __name__ == "__main__":
    main()
