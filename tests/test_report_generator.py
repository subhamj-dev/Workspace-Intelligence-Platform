import pytest
import json
import tempfile
from pathlib import Path

from tools.report_generator import ReportGenerator


class TestReportGenerator:
    def test_generate_report_creates_json(self):
        generator = ReportGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            generator.output_dir = tmpdir
            generator.add_metric("test_metric", 42)
            output = generator.generate_report("test_report.json")

            assert Path(output).exists()

            with open(output) as f:
                data = json.load(f)
                assert data["test_metric"] == 42

    def test_calculate_health_score_perfect(self):
        generator = ReportGenerator()
        score = generator.calculate_health_score(0, 0, 0)
        assert score == 100

    def test_calculate_health_score_clamped_to_zero(self):
        generator = ReportGenerator()
        score = generator.calculate_health_score(200, 0, 0)
        assert score == 0

    def test_calculate_health_score_partial(self):
        generator = ReportGenerator()
        score = generator.calculate_health_score(10, 5, 7)
        assert score == 78

    def test_generate_method_exists(self):
        generator = ReportGenerator()
        assert hasattr(generator, "generate")
        assert callable(generator.generate)
