import logging

logger = logging.getLogger("wip.plugins.pdf_plugin")


class Plugin:
    def __init__(self):
        self.config = {}

    def initialize(self):
        logger.info("PDF plugin initialized")
        self.config = {"enabled": True}
        self.pdf_support = False
        try:
            import PyPDF2
            self.pdf_support = True
            logger.info("PyPDF2 available for PDF extraction")
        except ImportError:
            logger.warning("PyPDF2 not available, PDF metadata extraction disabled")

    def process(self, metadata):
        if not self.config.get("enabled"):
            return {}

        if metadata.get("extension") != ".pdf":
            return {}

        enhancements = {}

        if self.pdf_support:
            try:
                import PyPDF2
                with open(metadata["path"], "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    enhancements["pdf_page_count"] = len(reader.pages)
                    info = reader.metadata
                    if info:
                        if info.title:
                            enhancements["pdf_title"] = info.title
                        if info.author:
                            enhancements["pdf_author"] = info.author
                        if info.subject:
                            enhancements["pdf_subject"] = info.subject
            except Exception as e:
                logger.error(f"Failed to extract PDF metadata: {e}")
                return {}
        else:
            enhancements["pdf_page_count"] = 0

        return enhancements

    def shutdown(self):
        logger.info("PDF plugin shutdown")
