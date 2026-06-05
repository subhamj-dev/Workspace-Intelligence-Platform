import logging

logger = logging.getLogger("wip.plugins.image_plugin")


class Plugin:
    def __init__(self):
        self.config = {}

    def initialize(self):
        logger.info("Image plugin initialized")
        self.config = {"enabled": True}
        self.exif_support = False
        try:
            from PIL import Image
            self.exif_support = True
            logger.info("Pillow available for image metadata extraction")
        except ImportError:
            logger.warning("Pillow not available, image metadata extraction disabled")

    def process(self, metadata):
        if not self.config.get("enabled"):
            return {}

        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
        if metadata.get("extension") not in image_extensions:
            return {}

        enhancements = {}

        if self.exif_support:
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS

                with Image.open(metadata["path"]) as img:
                    enhancements["image_width"] = img.width
                    enhancements["image_height"] = img.height
                    enhancements["image_format"] = img.format
                    enhancements["image_mode"] = img.mode

                    exif_data = img.getexif()
                    if exif_data:
                        for tag_id, value in exif_data.items():
                            tag_name = TAGS.get(tag_id, tag_id)
                            if tag_name in ("DateTimeOriginal", "Make", "Model"):
                                key = f"exif_{tag_name.lower()}"
                                enhancements[key] = str(value)
            except Exception as e:
                logger.error(f"Failed to extract image metadata: {e}")
                return {}

        return enhancements

    def shutdown(self):
        logger.info("Image plugin shutdown")
