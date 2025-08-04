from .BaseController import BaseController
from .ProjectController import ProjectController
from helpers.config import get_settings, Settings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class ProcessFileController(BaseController):
    """
    Controller for processing files.
    """

    def __init__(self, project_id: str):
        """
        Initialize the ProcessFileController.
        """
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id)
        
    def get_file_extension(self, file_name: str) -> str:
        """
        Get the file extension from the file name.
        """
        return os.path.splitext(file_name)[-1].lower()
    
    def get_file_loader(self, file_name: str):
        """
        Get the appropriate data loader based on the file type.
        """
        file_extension = self.get_file_extension(file_name)
        file_path = os.path.join(self.project_path, file_name)
        
        if file_extension in ['.pdf']:
            return PyMuPDFLoader(file_path, encoding='utf-8')
        elif file_extension in ['.txt']:
            return TextLoader(file_path, encoding='utf-8')
        else:
            return None
        
    def get_file_content(self, file_name: str):
        """
        Get the content of the file.
        """
        return self.get_file_loader(file_name).load() if self.get_file_loader(file_name) else None

    def process_file_into_chunks(self, file_content: list, chunk_size: int = 100, chunk_overlap: int = 20):
        """
        Process the file content into chunks.
        """
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        texts_list = [
            rec.page_content for rec in file_content if hasattr(rec, 'page_content') and rec.page_content.strip() != ''
        ]
        
        metadata_list = [
            rec.metadata for rec in file_content if hasattr(rec, 'metadata') and rec.page_content.strip() != ''
        ]
        
        
        chunks = text_splitter.create_documents(
            texts=texts_list,
            metadatas=metadata_list
        )
        
        return chunks
