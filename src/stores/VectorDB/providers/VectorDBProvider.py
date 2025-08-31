from abc import ABC, abstractmethod
from qdrant_client.models import PointStruct, Distance, VectorParams
from typing import List, Dict

class VectorDBProviderInterface(ABC):
    
    @abstractmethod
    def init_connection(self, db_path):
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def collection_exist(self, collection_name: str):
        pass
    
    @abstractmethod
    def list_all_collections(self):
        pass
    
    @abstractmethod
    def get_collection_info(self, collection_name: str):
        pass
    
    @abstractmethod
    def create_collection(self, collection_name: str, vectors_config: VectorParams):
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass
    
    @abstractmethod
    def insert_vector(self, collection_name: str, vector: List, metadata: dict = None):
        pass
    
    @abstractmethod
    def insert_many_vectors(self, collection_name: str, vectors: List, texts: List[str], metadatas: List[dict]):
        pass
    
    @abstractmethod
    def delete_vector(self, vector_id):
        pass
    
    @abstractmethod
    def search(self, collection_name: str, query_vector: List, top_k: int = 5):
        pass
    
    @abstractmethod
    def clear_db():
        pass
    