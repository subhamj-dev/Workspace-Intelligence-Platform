import hashlib
from collections import defaultdict


class DuplicateDetector:
    def __init__(self, config=None, audit_logger=None, quarantine_manager=None):
        self.config = config or {}
        self.audit_logger = audit_logger
        self.quarantine_manager = quarantine_manager
        self.hash_chunk_size = self.config.get("hash_chunk_size", 8192)

    def find_duplicates(self, files):
        hash_map = defaultdict(list)

        for file_meta in files:
            hash_map[file_meta["sha256"]].append(file_meta)

        duplicates = {
            file_hash: group
            for file_hash, group in hash_map.items()
            if len(group) > 1
        }

        return duplicates

    def process_duplicates(self, duplicates, quarantine_dir=None):
        results = []

        for file_hash, group in duplicates.items():
            group_sorted = sorted(group, key=lambda f: f.get("created", 0))
            original = group_sorted[0]
            duplicates_list = group_sorted[1:]

            for dup in duplicates_list:
                if self.quarantine_manager and quarantine_dir:
                    self.quarantine_manager.quarantine_file(
                        dup["path"], quarantine_dir, reason="duplicate"
                    )

                if self.audit_logger:
                    self.audit_logger.log(
                        action="QUARANTINE",
                        source=dup["path"],
                        destination=str(quarantine_dir) if quarantine_dir else "quarantine",
                        reason=f"duplicate_of:{original['path']}"
                    )

                results.append({
                    "original": original["path"],
                    "duplicate": dup["path"],
                    "hash": file_hash
                })

        return results

    def calculate_hash(self, file_path):
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(self.hash_chunk_size):
                sha.update(chunk)
        return sha.hexdigest()
