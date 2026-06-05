import json
from pathlib import Path


class WorkspaceHealth:
    def __init__(self, config=None):
        self.config = config or {}
        self.large_file_threshold_mb = self.config.get(
            "large_file_threshold_mb", 500
        )
        self.duplicate_penalty_per_group = self.config.get(
            "duplicate_penalty_per_group", 5
        )
        self.orphan_penalty_per_file = self.config.get(
            "orphan_penalty_per_file", 2
        )
        self.large_file_penalty_per_file = self.config.get(
            "large_file_penalty_per_file", 1
        )

    def calculate_health_score(self, files, duplicates, organized_dirs=None):
        duplicate_penalty = (
            len(duplicates) * self.duplicate_penalty_per_group
        )

        orphan_penalty = self._count_orphans(files, organized_dirs) * self.orphan_penalty_per_file

        large_file_penalty = (
            self._count_large_files(files) * self.large_file_penalty_per_file
        )

        score = 100 - duplicate_penalty - orphan_penalty - large_file_penalty
        return max(0, min(100, score))

    def _count_orphans(self, files, organized_dirs=None):
        if not organized_dirs:
            return 0

        organized_set = set(organized_dirs)
        count = 0

        for file_meta in files:
            parent = Path(file_meta["parent"])
            if not any(
                str(parent).startswith(d) for d in organized_set
            ):
                count += 1

        return count

    def _count_large_files(self, files):
        threshold_bytes = self.large_file_threshold_mb * 1024 * 1024
        return sum(1 for f in files if f["size"] > threshold_bytes)

    def generate_health_report(self, files, duplicates, organized_dirs=None):
        score = self.calculate_health_score(files, duplicates, organized_dirs)

        return {
            "health_score": score,
            "duplicate_penalty": len(duplicates) * self.duplicate_penalty_per_group,
            "orphan_penalty": self._count_orphans(files, organized_dirs) * self.orphan_penalty_per_file,
            "large_file_penalty": self._count_large_files(files) * self.large_file_penalty_per_file,
            "total_files": len(files),
            "duplicate_groups": len(duplicates),
            "large_files_count": self._count_large_files(files)
        }
