import json
import shutil
from pathlib import Path


class Organizer:
    def __init__(self, config=None, audit_logger=None):
        self.config = config or {}
        self.audit_logger = audit_logger
        self.dry_run = self.config.get("dry_run", True)
        self.rules = []
        self.default_destination = self.config.get(
            "default_destination", "miscellaneous"
        )

    def load_rules(self, rules_path):
        with open(rules_path) as f:
            data = json.load(f)
        self.rules = sorted(data.get("rules", []), key=lambda r: r.get("priority", 999))
        self.default_destination = data.get("default_destination", "miscellaneous")

    def organize(self, files, workspace_root):
        actions = []

        for file_meta in files:
            destination = self._match_rule(file_meta)

            if destination is None:
                continue

            source_path = Path(file_meta["path"])
            dest_path = Path(workspace_root) / destination / source_path.name

            if source_path == dest_path:
                continue

            actions.append({
                "source": str(source_path),
                "destination": str(dest_path),
                "reason": f"matched_rule:{self._rule_name_for(file_meta)}"
            })

            if not self.dry_run:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(dest_path))

                if self.audit_logger:
                    self.audit_logger.log(
                        action="MOVE",
                        source=str(source_path),
                        destination=str(dest_path),
                        reason=actions[-1]["reason"]
                    )

        return actions

    def _match_rule(self, file_meta):
        for rule in self.rules:
            rule_type = rule.get("type")

            if rule_type == "extension":
                if file_meta["extension"] in rule.get("extensions", []):
                    return rule["destination"]

            elif rule_type == "size":
                size_mb = file_meta["size"] / (1024 * 1024)
                min_size = rule.get("min_size_mb", 0)
                if size_mb >= min_size:
                    return rule["destination"]

        return self.default_destination

    def _rule_name_for(self, file_meta):
        for rule in self.rules:
            rule_type = rule.get("type")
            if rule_type == "extension":
                if file_meta["extension"] in rule.get("extensions", []):
                    return f"{rule_type}:{','.join(rule['extensions'])}"
            elif rule_type == "size":
                size_mb = file_meta["size"] / (1024 * 1024)
                if size_mb >= rule.get("min_size_mb", 0):
                    return f"{rule_type}:{rule['min_size_mb']}mb"
        return "default"
