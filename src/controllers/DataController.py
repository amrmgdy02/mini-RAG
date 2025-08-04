from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal

class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_file(self, file: UploadFile):
        allowed_types = self.app_settings.ALLOWED_FILE_TYPES
        max_size_mb = self.app_settings.MAX_FILE_SIZE_MB

        if file.content_type not in allowed_types:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED

        if file.size > max_size_mb * 1024 * 1024:  # convert file size to bytes
            return False, ResponseSignal.FILE_SIZE_EXCEEDED

        return True, ResponseSignal.FILE_VALIDATED_SUCCESS