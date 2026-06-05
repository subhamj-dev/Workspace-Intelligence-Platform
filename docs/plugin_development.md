# Plugin Development Guide

## Overview

Plugins extend the core functionality of the Workspace Intelligence Platform by adding metadata extraction capabilities, custom classification logic, and specialized processing. This guide documents the plugin API, development workflow, and best practices.

## Plugin Interface

Every plugin must expose a class named `Plugin` that implements the following interface:

```python
class Plugin:
    def initialize(self):
        pass

    def process(self, metadata):
        pass

    def shutdown(self):
        pass
```

### `initialize(self)`

Called once when the plugin is loaded at system startup. Use this method to:

- Load plugin-specific configuration
- Initialize external libraries or tools
- Open persistent connections or file handles
- Validate that required dependencies are available
- Set up logging for the plugin

**Parameters**: None

**Returns**: None

**Error handling**: Raise an exception if initialization fails. The system will log the error, disable the plugin for the current session, and continue loading other plugins.

**Example**:

```python
def initialize(self):
    import os
    self.config_path = os.environ.get("WIP_PLUGIN_CONFIG", "config/plugin_config.json")
    with open(self.config_path) as f:
        self.config = json.load(f)
```

### `process(self, metadata)`

Called for each file during the scanning pipeline. This method should extract or compute additional metadata for the given file and return it as a dictionary.

**Parameters**:

- `metadata` (dict): A dictionary containing the file's existing metadata. The following keys are guaranteed to be present:
  - `path` (str): Absolute path to the file
  - `filename` (str): File name with extension
  - `extension` (str): Lowercase file extension including the dot
  - `size` (int): File size in bytes
  - `created` (str): ISO 8601 creation timestamp
  - `modified` (str): ISO 8601 modification timestamp
  - `sha256` (str): Hexadecimal SHA256 hash
  - `parent` (str): Absolute path of parent directory
  - `mime_type` (str): Detected MIME type

**Returns**: A dictionary containing additional metadata fields. Return an empty dictionary if the plugin cannot process the file. The returned dictionary will be merged into the file's metadata record. Keys should use `lowercase_with_underscores` naming.

**Error handling**: Catch exceptions internally and log them. Return an empty dictionary on failure rather than raising an exception. The system will not fail if a plugin's `process` method raises an exception, but the exception will be logged and the plugin may be disabled if errors are repeated.

**Example**:

```python
def process(self, metadata):
    try:
        if metadata["extension"] != ".pdf":
            return {}

        extra = {
            "pdf_page_count": self._count_pages(metadata["path"]),
            "pdf_has_text": self._check_has_text(metadata["path"])
        }
        return extra
    except Exception as e:
        logging.getLogger(__name__).error(
            f"PDF plugin failed for {metadata['path']}: {e}"
        )
        return {}
```

### `shutdown(self)`

Called once when the system is shutting down. Use this method to:

- Close open connections or file handles
- Flush buffers and write pending data
- Release external resources
- Save plugin state if applicable

**Parameters**: None

**Returns**: None

**Error handling**: Raise an exception if shutdown fails. The system will log the error but will not prevent system shutdown.

## Expected Return Values

The `process` method should return a dictionary where:

- **Keys** are strings using `lowercase_with_underscores` naming
- **Values** are one of the following types:
  - `str`: String values
  - `int`: Integer values
  - `float`: Float values
  - `bool`: Boolean values
  - `list`: Lists of strings, integers, or floats
  - `dict`: Nested dictionaries (limit to one level of nesting)
  - `None`: Null values

Avoid returning large values (more than 1 KB per key) or deeply nested structures.

## Logging Requirements

Plugins must use Python's standard `logging` module for all log messages. The logger name should follow the convention `wip.plugins.{plugin_name}`.

Example:

```python
import logging

logger = logging.getLogger("wip.plugins.metadata_plugin")

class Plugin:
    def process(self, metadata):
        logger.info(f"Processing {metadata['filename']}")
        return {}
```

Log levels should be used appropriately:

- `DEBUG`: Detailed diagnostic information for development
- `INFO`: Normal operational messages (file processed, plugin initialized)
- `WARNING`: Unexpected but non-critical situations (missing optional data)
- `ERROR`: Errors that prevent processing of a specific file
- `CRITICAL`: Errors that prevent the plugin from functioning at all

## State Management

Plugins should be stateless whenever possible. Each call to `process` should be independent of previous calls. This ensures:

- The plugin can be safely parallelized
- Plugin failures do not corrupt accumulated state
- The plugin produces deterministic results

If a plugin requires persistent state:

1. Store state in the plugin's data directory at `data/plugins/{plugin_name}/`
2. Use the `initialize` method to load state and `shutdown` to save it
3. Document the state format and dependencies in the plugin's documentation
4. Initialize state to safe defaults if the state file is missing or corrupt

## Testing Plugins

Test plugins by instantiating the `Plugin` class and calling methods directly:

```python
def test_metadata_plugin():
    plugin = Plugin()
    plugin.initialize()

    result = plugin.process({
        "path": "/tmp/test.txt",
        "filename": "test.txt",
        "extension": ".txt",
        "size": 100,
        "created": "2026-01-01T00:00:00Z",
        "modified": "2026-01-01T00:00:00Z",
        "sha256": "abc123",
        "parent": "/tmp",
        "mime_type": "text/plain"
    })

    assert isinstance(result, dict)
    plugin.shutdown()
```

## Security Requirements

Plugins must adhere to the same security model as the core platform:

1. **No external uploads**: Plugins must not transmit file contents or metadata to external systems.
2. **No code execution**: Plugins must not execute user-provided content or evaluate dynamic code.
3. **No permanent deletion**: Plugins must not delete files permanently.
4. **No credential logging**: Plugins must not log credentials, tokens, or secrets.
