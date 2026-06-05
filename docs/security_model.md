# Security Model

## Overview

The Workspace Intelligence Platform operates under a defensive security model that prioritizes data integrity, user privacy, and system safety. All design decisions are guided by the principle that the platform should never cause data loss, expose sensitive information, or perform irreversible actions without explicit user consent.

## Core Principles

### No Permanent Deletion

The platform must never issue permanent file deletion operations. All file removal operations use a quarantine-based approach where files are moved to a designated quarantine directory rather than being deleted from the filesystem. The quarantine system preserves files for a configurable retention period, after which manual review is required before any permanent removal.

This principle applies to:

- Duplicate file handling
- Orphaned file cleanup
- Temporary file management
- Cache and working directory cleanup

### No External Uploads

The platform operates exclusively on the local machine. No file contents, metadata, derived data, usage statistics, or telemetry information may be transmitted to external systems. This prohibition covers:

- HTTP requests to remote servers
- DNS lookups that could leak workspace information
- Embedded analytics or tracking in plugin code
- Crash reporting services that transmit stack traces containing file paths
- License validation services that checksum workspace contents

The only exception is user-initiated export operations, where the user explicitly selects files for export and confirms the operation.

### Immutable Audit Logs

All audit log records are immutable once written. The system maintains the integrity of the audit log through the following mechanisms:

1. **Append-only writes**: Log records are appended to a JSON Lines file. Records are never modified, deleted, or reordered.

2. **Hash chaining**: Each log record includes the SHA256 hash of the previous record, forming a hash chain. This allows detection of tampering with historical records.

3. **Integrity verification**: The system provides a command to verify audit log integrity by recomputing the hash chain and comparing it with the stored chain.

4. **Read-only access**: The audit log file is opened in append mode during normal operation. Processes and plugins cannot modify existing records.

### Manual Approval Workflow

Certain operations require explicit user approval before execution. These operations include:

1. **Rule activation**: New organizational rules are applied in dry-run mode by default. Users must review the predicted impact and confirm activation.

2. **Quarantine removal**: Users must confirm before files are permanently removed from quarantine. The system provides a summary of files to be removed, including their original paths and quarantine dates.

3. **Configuration changes**: Changes to security-sensitive configuration options (quarantine retention, excluded directories, hash algorithm) require user confirmation.

4. **Plugin installation**: New plugins are disabled by default. Users must explicitly enable plugins after reviewing their capabilities and permissions.

## Threat Model

### In-Scope Threats

The platform defends against the following threats:

1. **Accidental data loss**: Users accidentally deleting files through automation. Mitigated by the quarantine system and manual approval workflow.

2. **Configuration errors**: Incorrect organizational rules causing files to be moved to wrong locations. Mitigated by dry-run mode and audit logging.

3. **Plugin malfunctions**: Plugins behaving unexpectedly due to bugs or incompatible updates. Mitigated by plugin error isolation and the disable-on-failure mechanism.

4. **Workspace corruption**: File system errors or concurrent modifications causing inconsistent state. Mitigated by the two-phase scan-then-act approach.

### Out-of-Scope Threats

The following threats are outside the platform's security model:

1. **Malicious plugins**: Plugins intentionally designed to exfiltrate data or damage files. The platform does not sandbox plugins at the OS level.

2. **Filesystem-level attacks**: Attacks that modify files or metadata outside of WIP's control. The platform cannot defend against direct filesystem manipulation.

3. **Privilege escalation**: Attacks that use WIP to gain elevated privileges. The platform operates with user-level privileges and does not request elevation.

4. **Side-channel attacks**: Timing or resource-usage attacks that infer workspace contents. The platform does not implement side-channel countermeasures.

## Configuration Security

Configuration files must be protected according to the following guidelines:

1. **File permissions**: Configuration files should be readable only by the owning user (`chmod 600` on Unix systems).

2. **Sensitive data**: Credentials, API keys, and tokens must never appear in configuration files. Use environment variables or a secure credential store for sensitive values.

3. **Validation**: Configuration files are validated at load time. Invalid configurations are rejected with descriptive error messages.

4. **Backup**: Configuration files should be included in the user's backup strategy. The platform does not automatically backup configuration files.

## Audit Log Integrity Verification

The audit log uses a hash chain to detect tampering. Each record contains a `previous_hash` field that stores the SHA256 hash of the preceding record. The first record in the log has a `previous_hash` of all zeros.

To verify the integrity of an audit log:

```python
import hashlib
import json

def verify_audit_log(log_path):
    previous_hash = "0" * 64

    with open(log_path) as f:
        for line in f:
            record = json.loads(line)

            if record["previous_hash"] != previous_hash:
                return False

            record_hash = hashlib.sha256(
                json.dumps(record, sort_keys=True).encode()
            ).hexdigest()

            previous_hash = record_hash

    return True
```

## Incident Response

If a security incident is detected (such as evidence of audit log tampering or unauthorized file modification):

1. The system logs the incident and alerts the user.
2. The platform enters a restricted mode where only read operations are permitted.
3. A full audit log verification is performed.
4. The user is guided through the recovery process.
