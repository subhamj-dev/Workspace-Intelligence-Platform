import json
from collections import Counter, defaultdict
from pathlib import Path


class StatisticsExporter:
    def __init__(self, config=None):
        self.config = config or {}

    def compute_file_type_distribution(self, files):
        extension_counts = Counter()
        mime_counts = Counter()
        extension_sizes = defaultdict(int)

        for file_meta in files:
            ext = file_meta.get("extension", "unknown")
            mime = file_meta.get("mime_type", "application/octet-stream")
            size = file_meta.get("size", 0)

            extension_counts[ext] += 1
            mime_counts[mime] += 1
            extension_sizes[ext] += size

        return {
            "by_extension": dict(extension_counts.most_common()),
            "by_mime_type": dict(mime_counts.most_common()),
            "total_files": len(files),
            "total_size_bytes": sum(f["size"] for f in files)
        }

    def compute_largest_files(self, files, count=50):
        sorted_files = sorted(files, key=lambda f: f.get("size", 0), reverse=True)
        return [
            {
                "path": f["path"],
                "filename": f["filename"],
                "size_bytes": f["size"],
                "size_mb": round(f["size"] / (1024 * 1024), 2),
                "mime_type": f.get("mime_type", "unknown"),
                "modified": f.get("modified", "")
            }
            for f in sorted_files[:count]
        ]

    def compute_recently_modified(self, files, count=50):
        sorted_files = sorted(
            files, key=lambda f: f.get("modified", 0), reverse=True
        )
        return [
            {
                "path": f["path"],
                "filename": f["filename"],
                "size_bytes": f["size"],
                "modified": f.get("modified", ""),
                "extension": f.get("extension", "")
            }
            for f in sorted_files[:count]
        ]

    def export_statistics(self, files, output_path):
        stats = {
            "file_type_distribution": self.compute_file_type_distribution(files),
            "largest_files": self.compute_largest_files(
                files, self.config.get("max_largest_files", 50)
            ),
            "recently_modified": self.compute_recently_modified(
                files, self.config.get("max_recent_files", 50)
            ),
            "total_size_mb": round(
                sum(f["size"] for f in files) / (1024 * 1024), 2
            ),
            "average_file_size_kb": round(
                (sum(f["size"] for f in files) / len(files)) / 1024
                if files else 0, 1
            )
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(stats, f, indent=4)

        return str(output_path)
