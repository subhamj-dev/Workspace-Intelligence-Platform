import shutil
from pathlib import Path
from datetime import datetime, timedelta


class QuarantineManager:
    def __init__(self, config=None, audit_logger=None):
        self.config = config or {}
        self.audit_logger = audit_logger
        self.retention_days = self.config.get("retention_days", 30)

    def quarantine_file(self, file_path, quarantine_dir, reason="unspecified"):
        src = Path(file_path)
        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        quarantine_path = Path(quarantine_dir)
        quarantine_path.mkdir(parents=True, exist_ok=True)

        dest = quarantine_path / src.name
        if dest.exists():
            stem = dest.stem
            suffix = dest.suffix
            dest = quarantine_path / f"{stem}_{src.stat().st_mtime}{suffix}"

        shutil.move(str(src), str(dest))

        if self.audit_logger:
            self.audit_logger.log(
                action="QUARANTINE",
                source=str(src),
                destination=str(dest),
                reason=reason
            )

        return str(dest)

    def list_quarantined(self, quarantine_dir):
        qpath = Path(quarantine_dir)
        if not qpath.exists():
            return []

        files = []
        for path in qpath.iterdir():
            if path.is_file():
                files.append({
                    "path": str(path),
                    "name": path.name,
                    "size": path.stat().st_size,
                    "quarantined_date": datetime.fromtimestamp(
                        path.stat().st_ctime
                    ).isoformat()
                })
        return files

    def find_expired(self, quarantine_dir):
        qpath = Path(quarantine_dir)
        if not qpath.exists():
            return []

        cutoff = datetime.now() - timedelta(days=self.retention_days)
        expired = []

        for path in qpath.iterdir():
            if path.is_file():
                qdate = datetime.fromtimestamp(path.stat().st_ctime)
                if qdate < cutoff:
                    expired.append({
                        "path": str(path),
                        "name": path.name,
                        "quarantined_date": qdate.isoformat(),
                        "expired_since": (cutoff - qdate).days
                    })
        return expired

    def restore_file(self, quarantined_path, original_path=None):
        src = Path(quarantined_path)
        if not src.exists():
            raise FileNotFoundError(f"Quarantined file not found: {quarantined_path}")

        if original_path:
            dest = Path(original_path)
        else:
            dest = Path.cwd() / src.name

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))

        if self.audit_logger:
            self.audit_logger.log(
                action="RESTORE",
                source=str(src),
                destination=str(dest),
                reason="manual_restore"
            )

        return str(dest)

    def remove_file(self, quarantined_path):
        src = Path(quarantined_path)
        if not src.exists():
            raise FileNotFoundError(f"Quarantined file not found: {quarantined_path}")

        src.unlink()

        if self.audit_logger:
            self.audit_logger.log(
                action="DELETE",
                source=str(src),
                destination="",
                reason="manual_removal"
            )
