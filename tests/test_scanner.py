import pytest
import tempfile
from pathlib import Path

from core.scanner import Scanner


@pytest.fixture
def temp_workspace():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "documents").mkdir()
        (Path(tmpdir) / "documents" / "report.pdf").write_text("pdf content")
        (Path(tmpdir) / "documents" / "notes.txt").write_text("notes content")
        (Path(tmpdir) / "images").mkdir()
        (Path(tmpdir) / "images" / "photo.jpg").write_text("image content")
        yield tmpdir


class TestScanner:
    def test_scan_returns_all_files(self, temp_workspace):
        scanner = Scanner()
        files = scanner.scan(temp_workspace)
        assert len(files) == 3

    def test_scan_collects_metadata(self, temp_workspace):
        scanner = Scanner()
        files = scanner.scan(temp_workspace)

        for file_meta in files:
            assert "path" in file_meta
            assert "filename" in file_meta
            assert "extension" in file_meta
            assert "size" in file_meta
            assert "sha256" in file_meta
            assert "parent" in file_meta
            assert "mime_type" in file_meta

    def test_scan_computes_sha256(self, temp_workspace):
        scanner = Scanner()
        files = scanner.scan(temp_workspace)
        pdf_file = [f for f in files if f["filename"] == "report.pdf"][0]
        assert len(pdf_file["sha256"]) == 64

    def test_scan_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = Scanner()
            files = scanner.scan(tmpdir)
            assert len(files) == 0

    def test_scan_exclude_patterns(self, temp_workspace):
        scanner = Scanner({"exclude_patterns": ["*.txt"]})
        files = scanner.scan(temp_workspace)
        assert len(files) == 2
        assert all(f["extension"] != ".txt" for f in files)
