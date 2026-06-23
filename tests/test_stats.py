import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

from eval_engine.stats import wilson_interval, confidence_band


class TestWilsonInterval:
    """Tests for the Wilson score confidence interval."""

    def test_known_case_13_of_15(self):
        """13/15 passes → interval should be approximately (0.6367, 0.9717)."""
        low, high = wilson_interval(13, 15)
        # Manually computed Wilson interval for p̂=0.8667, n=15, z=1.96:
        # centre = (0.8667 + 1.9208/30) / (1 + 3.8416/15) = 0.9307 / 1.2561 ≈ 0.8075 (adjusted)
        # The exact Wilson interval for 13/15 at 95% is approximately (0.6194, 0.9622)
        assert 0.58 < low < 0.68, f"Lower bound {low} out of expected range"
        assert 0.93 < high < 1.0, f"Upper bound {high} out of expected range"
        assert low < high

    def test_all_pass(self):
        """10/10 passes → upper bound should be 1.0, lower bound > 0.5."""
        low, high = wilson_interval(10, 10)
        assert high == 1.0
        assert low > 0.5

    def test_none_pass(self):
        """0/10 passes → lower bound should be 0.0, upper bound < 0.5."""
        low, high = wilson_interval(0, 10)
        assert low == 0.0
        assert high < 0.5

    def test_zero_total(self):
        """n=0 → (0.0, 0.0) without raising."""
        low, high = wilson_interval(0, 0)
        assert low == 0.0
        assert high == 0.0

    def test_single_item_pass(self):
        """1/1 → should return valid interval."""
        low, high = wilson_interval(1, 1)
        assert 0.0 <= low <= 1.0
        assert 0.0 <= high <= 1.0
        assert low < high

    def test_large_sample(self):
        """90/100 → interval should be tight around 0.90."""
        low, high = wilson_interval(90, 100)
        assert 0.82 < low < 0.90
        assert 0.93 < high < 0.97
        # Width should be < 0.15 for n=100
        assert (high - low) < 0.15


class TestConfidenceBand:
    """Tests for the confidence band label function."""

    def test_small_sample(self):
        assert confidence_band(5) == "Indicative"
        assert confidence_band(1) == "Indicative"
        assert confidence_band(29) == "Indicative"

    def test_moderate_sample(self):
        assert confidence_band(30) == "Moderate"
        assert confidence_band(50) == "Moderate"
        assert confidence_band(99) == "Moderate"

    def test_high_sample(self):
        assert confidence_band(100) == "High"
        assert confidence_band(150) == "High"
        assert confidence_band(1000) == "High"

    def test_zero(self):
        assert confidence_band(0) == "Indicative"


class TestReportFields:
    """Tests that generate_report() includes all new fields."""

    def test_report_contains_new_fields(self):
        """Construct a runner with mock results and verify report schema."""
        from eval_engine.runners.base import BaseRunner, EvaluationResult

        with patch.object(BaseRunner, '_read_frontmatter'):
            runner = BaseRunner.__new__(BaseRunner)
            runner.loop_name = "test-loop"
            runner.tags = ["test", "unit"]
            runner.target_endpoint = "http://localhost:8080"
            runner.config_path = "config.yaml"
            runner.dataset_override = None
            runner.config = MagicMock()
            runner.config.target.type = "openai_compatible"
            runner.config.judge = None
            runner.config.dataset_path = None
            runner.judge_adapter = None
            runner.framework_mappings = ["OWASP-LLM03", "NIST-MEASURE-1"]
            runner.requires = []
            runner._dataset_row_count = 20
            runner._using_example_dataset = False
            runner.start_time = None
            runner.end_time = None
            runner.results = [
                EvaluationResult(metric="test_metric", score=0.85, passed=True, details="ok"),
                EvaluationResult(metric="test_metric_2", score=0.30, passed=False, details="fail"),
            ]

            report = runner.generate_report()

        # Verify all new fields are present
        assert "compliance_disclaimer" in report
        assert "Framework tags" in report["compliance_disclaimer"]
        assert "not certified compliance" in report["compliance_disclaimer"]

        assert "sample_size" in report
        assert report["sample_size"] == 20

        assert "coverage_note" in report
        assert "20 test items" in report["coverage_note"]
        assert "directional signal" in report["coverage_note"]

        assert "confidence_interval" in report
        assert isinstance(report["confidence_interval"], list)
        assert len(report["confidence_interval"]) == 2

        assert "confidence_band" in report
        assert report["confidence_band"] == "Indicative"  # n=20 < 30

        assert "maps_to" in report["metadata"]
        assert "OWASP-LLM03" in report["metadata"]["maps_to"]
        assert "NIST-MEASURE-1" in report["metadata"]["maps_to"]

        # Tags should still be the topical tags
        assert report["metadata"]["tags"] == ["test", "unit"]


class TestDatasetOverride:
    """Tests that dataset_override is respected by _load_dataset()."""

    def test_override_loads_custom_file(self):
        """Passing dataset_override should load that specific file."""
        from eval_engine.runners.base import BaseRunner

        # Create a temp JSONL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
            f.write('{"input": "test input", "expected": "test expected", "rubric": "test rubric"}\n')
            f.write('{"input": "test input 2", "expected": "test expected 2", "rubric": "test rubric 2"}\n')
            temp_path = f.name

        try:
            with patch.object(BaseRunner, '_read_frontmatter'):
                runner = BaseRunner.__new__(BaseRunner)
                runner.loop_name = "test-loop"
                runner.dataset_override = temp_path
                runner.config = MagicMock()
                runner.config.dataset_path = None
                runner._dataset_row_count = 0
                runner._using_example_dataset = False

                dataset = runner._load_dataset()

            assert len(dataset) == 2
            assert dataset[0]["input"] == "test input"
            assert runner._dataset_row_count == 2
            assert runner._using_example_dataset is False
        finally:
            os.unlink(temp_path)

    def test_example_dataset_sets_warning_flag(self):
        """When no override is given, _using_example_dataset should be True."""
        from eval_engine.runners.base import BaseRunner

        with patch.object(BaseRunner, '_read_frontmatter'):
            runner = BaseRunner.__new__(BaseRunner)
            runner.loop_name = "nonexistent-loop"
            runner.dataset_override = None
            runner.config = MagicMock()
            runner.config.dataset_path = None
            runner._dataset_row_count = 0
            runner._using_example_dataset = False

            dataset = runner._load_dataset()

        # No file exists for nonexistent-loop, so dataset is empty
        assert len(dataset) == 0
        assert runner._using_example_dataset is True
