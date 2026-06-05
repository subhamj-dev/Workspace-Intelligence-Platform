import pytest
import tempfile
from pathlib import Path

from core.duplicate_detector import DuplicateDetector


class TestDuplicateDetector:
    def test_find_duplicates_detects_identical_files(self):
        files = [
            {"sha256": "abc123", "path": "/a/file1.txt", "created": 1000},
            {"sha256": "abc123", "path": "/b/file2.txt", "created": 2000},
            {"sha256": "def456", "path": "/c/file3.txt", "created": 3000},
        ]

        detector = DuplicateDetector()
        duplicates = detector.find_duplicates(files)

        assert "abc123" in duplicates
        assert len(duplicates["abc123"]) == 2

    def test_find_duplicates_no_duplicates(self):
        files = [
            {"sha256": "abc123", "path": "/a/file1.txt", "created": 1000},
            {"sha256": "def456", "path": "/b/file2.txt", "created": 2000},
        ]

        detector = DuplicateDetector()
        duplicates = detector.find_duplicates(files)

        assert len(duplicates) == 0

    def test_calculate_hash_consistency(self):
        detector = DuplicateDetector()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as f:
            f.write("test content")
            f.flush()

            hash1 = detector.calculate_hash(f.name)
            hash2 = detector.calculate_hash(f.name)

            assert hash1 == hash2

    def test_calculate_hash_different_files(self):
        detector = DuplicateDetector()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as f1:
            f1.write("content a")
            f1.flush()

            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as f2:
                f2.write("content b")
                f2.flush()

                hash_a = detector.calculate_hash(f1.name)
                hash_b = detector.calculate_hash(f2.name)

                assert hash_a != hash_b
