from .base import BaseScorer, ScoreResult
from .exact_match import ExactMatchScorer
from .regex_match import RegexMatchScorer
from .latency_slo import LatencySloScorer
from .embedding_similarity import EmbeddingSimilarityScorer
from .code_exec import CodeExecScorer
from .llm_judge import LlmJudgeScorer

def get_scorer(scorer_type: str, judge_adapter=None, rubric: str = "", **kwargs) -> BaseScorer:
    if scorer_type == "exact_match":
        return ExactMatchScorer(**kwargs)
    elif scorer_type == "regex_match":
        return RegexMatchScorer(**kwargs)
    elif scorer_type == "latency_slo":
        return LatencySloScorer(**kwargs)
    elif scorer_type == "embedding_similarity":
        return EmbeddingSimilarityScorer(**kwargs)
    elif scorer_type == "code_exec":
        return CodeExecScorer(**kwargs)
    elif scorer_type == "llm_judge":
        return LlmJudgeScorer(judge_adapter=judge_adapter, rubric=rubric)
    else:
        raise ValueError(f"Unknown scorer type: {scorer_type}")
