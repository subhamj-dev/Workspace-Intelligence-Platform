import hashlib
from pathlib import Path


class Scanner:
    def __init__(self, config=None):
        self.config = config or {}
        self.hash_chunk_size = self.config.get("hash_chunk_size", 8192)
        self.large_file_threshold = self.config.get(
            "large_file_threshold", 1073741824
        )
        self.hash_large_files = self.config.get("hash_large_files", True)

    def scan(self, directory):
        files = []
        exclude_patterns = self.config.get("exclude_patterns", [])
        max_depth = self.config.get("max_depth", 0)
        follow_symlinks = self.config.get("follow_symlinks", False)

        for path in Path(directory).rglob("*"):
            if path.is_file():
                if self._should_exclude(path, exclude_patterns):
                    continue

                metadata = self._collect_metadata(path)
                files.append(metadata)

        return files

    def _should_exclude(self, path, patterns):
        for pattern in patterns:
            if path.match(pattern):
                return True
        return False

    def _collect_metadata(self, path):
        stat = path.stat()
        sha256_hash = self._compute_hash(path)

        return {
            "path": str(path.resolve()),
            "filename": path.name,
            "extension": path.suffix.lower(),
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "sha256": sha256_hash,
            "parent": str(path.parent.resolve()),
            "mime_type": self._detect_mime(path)
        }

    def _compute_hash(self, path):
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(self.hash_chunk_size):
                sha.update(chunk)
        return sha.hexdigest()

    def _detect_mime(self, path):
        try:
            import magic
            return magic.from_file(str(path), mime=True)
        except ImportError:
            extension_map = {
                ".pdf": "application/pdf",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".txt": "text/plain",
                ".md": "text/markdown",
                ".py": "text/x-python",
                ".json": "application/json",
                ".html": "text/html",
                ".zip": "application/zip",
            }
            return extension_map.get(path.suffix.lower(), "application/octet-stream")
