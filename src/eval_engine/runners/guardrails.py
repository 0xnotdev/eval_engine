import asyncio
from .evaluation import EvaluationRunner

class GuardrailsRunner(EvaluationRunner):
    """Runner for testing safety and boundary guardrails.
    Inherits dataset loading and scoring from EvaluationRunner, 
    but can be extended later for specific guardrail topologies."""
    pass
