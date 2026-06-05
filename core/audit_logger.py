import hashlib
import json
from datetime import datetime


class AuditLogger:
    def __init__(self, log_path="audit_log.jsonl"):
        self.log_path = log_path
        self.previous_hash = None
        self._load_last_hash()

    def _load_last_hash(self):
        try:
            with open(self.log_path) as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        record_str = json.dumps(record, sort_keys=True)
                        self.previous_hash = hashlib.sha256(
                            record_str.encode()
                        ).hexdigest()
        except FileNotFoundError:
            self.previous_hash = "0" * 64

    def log(self, action, source, destination, reason):
        record = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "action": action,
            "source": source,
            "destination": destination,
            "reason": reason,
            "previous_hash": self.previous_hash
        }

        record_str = json.dumps(record, sort_keys=True)
        self.previous_hash = hashlib.sha256(record_str.encode()).hexdigest()

        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        return record

    def verify_integrity(self):
        previous_hash = "0" * 64

        try:
            with open(self.log_path) as f:
                for line in f:
                    if not line.strip():
                        continue
                    record = json.loads(line)

                    if record.get("previous_hash", "") != previous_hash:
                        return False

                    record_str = json.dumps(
                        {k: v for k, v in record.items() if k != "previous_hash"},
                        sort_keys=True
                    )
                    previous_hash = hashlib.sha256(record_str.encode()).hexdigest()
            return True
        except FileNotFoundError:
            return True
