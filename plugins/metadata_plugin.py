import logging

logger = logging.getLogger("wip.plugins.metadata_plugin")


class Plugin:
    def __init__(self):
        self.config = {}

    def initialize(self):
        logger.info("Metadata plugin initialized")
        self.config = {"enabled": True}

    def process(self, metadata):
        if not self.config.get("enabled"):
            return {}

        enhancements = {}

        filename = metadata.get("filename", "")
        doc_keywords = ["report", "summary", "notes", "draft", "final"]
        name_lower = filename.lower()

        for keyword in doc_keywords:
            if keyword in name_lower:
                enhancements["document_type"] = keyword
                break

        size = metadata.get("size", 0)
        if size > 0:
            enhancements["size_mb"] = round(size / (1024 * 1024), 2)
            enhancements["size_kb"] = round(size / 1024, 1)

        return enhancements

    def shutdown(self):
        logger.info("Metadata plugin shutdown")
