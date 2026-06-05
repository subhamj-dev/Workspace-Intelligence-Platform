import json
from pathlib import Path


class ReportGenerator:
    def __init__(self, config=None):
        self.config = config or {}
        self.results = {}
        self.output_dir = self.config.get("output_directory", "reports")

    def add_metric(self, name, value):
        self.results[name] = value

    def generate(self, workspace_data):
        """
        TODO: Implement according to README.md

        Requirements (from README.md):
        - Health score calculation using formula:
          health_score = 100 - duplicate_penalty - orphan_penalty - large_file_penalty
        - Duplicate count report
        - File type distribution statistics
        - Largest files report (top N by size)
        - Recently modified files report
        - Output must be in JSON format

        The workspace_data parameter contains:
        - files: list of file metadata dictionaries
        - duplicates: duplicate detection results
        - actions: organizer actions taken
        - scan_stats: scanning statistics

        See README.md for complete specification.
        """
        pass

    def generate_report(self, output_file):
        output_path = Path(self.output_dir) / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=4)

        return str(output_path)

    def calculate_health_score(
        self,
        duplicate_penalty,
        orphan_penalty,
        large_file_penalty
    ):
        score = (
            100
            - duplicate_penalty
            - orphan_penalty
            - large_file_penalty
        )

        return max(0, min(100, score))


if __name__ == "__main__":
    report = ReportGenerator()

    report.add_metric("duplicate_files", 15)
    report.add_metric("large_files", 8)

    score = report.calculate_health_score(
        duplicate_penalty=10,
        orphan_penalty=5,
        large_file_penalty=7
    )

    report.add_metric("health_score", score)

    report.generate_report("workspace_report.json")
