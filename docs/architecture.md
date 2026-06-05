# System Architecture

## Overview

Workspace Intelligence Platform follows a pipeline architecture where data flows through distinct processing stages. Each stage has a well-defined responsibility and communicates with adjacent stages through clearly specified interfaces.

## Data Flow

```
                    ┌─────────────┐
                    │   Scanner   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Metadata   │
                    │  Pipeline   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Duplicate  │
                    │  Detection  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Organizer   │
                    │ Engine      │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Knowledge  │
                    │   Index     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Reporting  │
                    │   Engine    │
                    └─────────────┘
```

## Design Decisions

### Why SHA256?

SHA256 was chosen as the hash algorithm for duplicate detection for several reasons:

1. **Collision resistance**: SHA256 provides 128 bits of collision resistance, making accidental hash collisions statistically impossible for any realistic workspace size. The system assumes that matching SHA256 hashes indicate identical file contents.

2. **Determinism**: SHA256 produces identical output for identical input across all platforms and implementations. This ensures that hash values computed on different systems are directly comparable.

3. **Hardware acceleration**: Modern x86 processors include SHA-NI instructions that accelerate SHA256 computation. ARM processors in recent Apple Silicon and high-end Android devices also include hardware SHA256 support. This makes SHA256 competitive with faster but weaker hash algorithms in practice.

4. **Availability**: SHA256 is available in the Python standard library through the `hashlib` module with no additional dependencies required.

Alternative algorithms considered and rejected:

- **MD5**: Rejected due to known collision attacks and the availability of practical collision generation techniques.
- **SHA1**: Rejected due to the SHAttered collision attack and deprecation in security standards.
- **xxHash**: Rejected because non-cryptographic hashes may produce collisions that could trigger false duplicate detections.
- **BLAKE2**: A strong candidate, but rejected because it is not available in the Python standard library without additional dependencies.

### Why Quarantine Instead of Delete?

The quarantine system was chosen over permanent deletion for several reasons:

1. **User safety**: Accidental duplicate detection is possible if a file is modified between scans (a hash change would prevent detection, but a false positive could occur with files that have identical hashes but different semantic content). Quarantine provides a safety net for such cases.

2. **Recoverability**: Users may discover that a "duplicate" file was actually needed after it has been moved. Quarantine preserves these files for a configurable retention period, during which users can restore them.

3. **Audit trail**: Moving files to quarantine creates an audit record that documents the action, the original location, and the reason. This provides a complete history that would be lost with permanent deletion.

4. **Regulatory compliance**: Some regulatory frameworks require that files not be permanently deleted without a review period. Quarantine satisfies this requirement without requiring users to understand compliance rules.

### Why JSON for Reports?

JSON was chosen as the report format for the following reasons:

1. **Human readability**: JSON files can be read and understood without specialized tools.
2. **Wide tooling support**: Every programming language and many command-line tools can parse JSON.
3. **Schema flexibility**: JSON accommodates nested and variable-structure data without requiring schema evolution management.
4. **Streaming parsing**: Large JSON arrays can be parsed incrementally without loading the entire file into memory.

Alternative formats considered and rejected:

- **CSV**: Rejected because it does not support nested structures needed for complex report types like duplicate groups.
- **Protocol Buffers**: Rejected because they require schema compilation and produce binary output that is not human-readable.
- **SQLite**: Rejected because SQLite files are not easily shareable or human-readable.

## Module Dependencies

```
scanner → metadata_pipeline → duplicate_detector → organizer → knowledge_index → reporting_engine
```

Each module depends only on the module immediately preceding it in the pipeline. No module depends on a downstream module. This ensures that the pipeline can be truncated for testing or debugging purposes.

## Threading Model

The platform uses a single-threaded execution model by default. This simplifies development, debugging, and auditing. Plugin processing is the only stage that may be parallelized, and parallelization is opt-in at the plugin level.

## Data Storage

The platform stores data in the following locations:

| Data | Storage | Location |
|------|---------|----------|
| File metadata | SQLite | `data/index.db` |
| Audit logs | JSON Lines | `data/audit_log.jsonl` |
| Quarantined files | Filesystem | `quarantine/` |
| Reports | JSON | `reports/` |
| Plugin data | Filesystem | `data/plugins/{plugin_name}/` |

## Error Handling

Errors in any pipeline stage follow this protocol:

1. The error is logged with a unique error code.
2. The file causing the error is skipped and recorded in an error report.
3. The pipeline continues processing remaining files.
4. A summary of errors is included in the final report.
