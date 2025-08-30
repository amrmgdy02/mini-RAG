from enum import Enum

class ResponseSignal(Enum):
    
    FILE_VALIDATED_SUCCESS = "file_validate_successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    FILE_PROCESS_SUCCESS = "file_process_success"
    FILE_PROCESS_FAILED = "file_process_failed"
    CHUNK_EMBEDDING_SUCCESS = "chunk_embedding_success"
    CHUNK_EMBEDDING_FAILED = "chunk_embedding_failed"
    FILE_PROCESSING_SUCCESS = "file_processing_success"