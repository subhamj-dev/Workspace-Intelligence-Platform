import pytest
import json
import tempfile
from pathlib import Path

from core.organizer import Organizer


@pytest.fixture
def rules_file():
    rules = {
        "rules": [
            {
                "priority": 1,
                "type": "extension",
                "extensions": [".pdf"],
                "destination": "documents"
            },
            {
                "priority": 2,
                "type": "extension",
                "extensions": [".jpg"],
                "destination": "images"
            }
        ],
        "default_destination": "miscellaneous"
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(rules, f)
        rules_path = f.name

    yield rules_path
    Path(rules_path).unlink(missing_ok=True)


class TestOrganizer:
    def test_load_rules(self, rules_file):
        organizer = Organizer()
        organizer.load_rules(rules_file)
        assert len(organizer.rules) == 2

    def test_match_rule_by_extension(self, rules_file):
        organizer = Organizer()
        organizer.load_rules(rules_file)

        file_meta = {"extension": ".pdf", "size": 1000}
        dest = organizer._match_rule(file_meta)
        assert dest == "documents"

    def test_default_destination(self, rules_file):
        organizer = Organizer()
        organizer.load_rules(rules_file)

        file_meta = {"extension": ".xyz", "size": 1000}
        dest = organizer._match_rule(file_meta)
        assert dest == "miscellaneous"

    def test_organize_dry_run(self, rules_file):
        organizer = Organizer({"dry_run": True})
        organizer.load_rules(rules_file)

        files = [
            {"path": "/tmp/report.pdf", "extension": ".pdf", "size": 1000}
        ]

        actions = organizer.organize(files, "/tmp")
        assert len(actions) == 1
        assert actions[0]["reason"].startswith("matched_rule")
