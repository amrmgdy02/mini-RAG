from .VectorDBProvider import VectorDBProviderInterface
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from helpers.config import get_settings, Settings
from typing import List, Dict
import uuid
import logging

class QdrantProvider(VectorDBProviderInterface):
    def __init__(self, db_path):
        self.client = None
        self.db_path = db_path
        self.app_settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
    def init_connection(self):
        # remember the problem of local mode (celery and fastAPI can't access db concurrently)
        self.client = QdrantClient(host=self.app_settings.QDRANT_HOST, port=self.app_settings.QDRANT_PORT)
        
    def disconnect(self):
        self.client = None
    
    def collection_exist(self, collection_name: str):
        if not self.client:
            raise ConnectionError("Not connected to database")
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List[str]:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def create_collection(self, collection_name: str, vectors_config: VectorParams):
        if self.collection_exist(collection_name=collection_name):
            return False
        
        return self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=vectors_config,
                )
        
    def delete_collection(self, collection_name: str):
        if self.collection_exist(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)
    
        
    def insert_vector(self, collection_name: str, vector: List, metadata: dict = None):
        if not self.collection_exist(collection_name=collection_name):
            return False
        
        try:
            points = [
                PointStruct(id=str(uuid.uuid4()), vector=vector, payload=metadata),
            ]
            
            operation_info = self.client.upsert(
                collection_name=collection_name,
                wait=True,
                points=points
            )
            
            return operation_info
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return None
        
        
    def insert_many_vectors(self, collection_name: str, vectors: List, texts: List[str], metadatas: List[dict]):
        
        try:
            points = [
                PointStruct(id=str(uuid.uuid4()), vector=vector, payload={"text": text, "metadata": metadata})
                for vector, text, metadata in zip(vectors, texts, metadatas)
            ]
            
            operation_info = self.client.upsert(
                collection_name=collection_name,
                wait=True,
                points=points
            )
            
            return operation_info
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return None
        
    
    def search(self, collection_name: str, query_vector: List, top_k: int = 5) -> List[dict]:
        if not self.collection_exist(collection_name=collection_name):
            raise ValueError(f"Collection '{collection_name}' does not exist")

        try:

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )
            
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                for hit in results
            ]
    
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return []
        
    def delete_vector(self, collection_name: str, vector_id):
        if not self.collection_exist(collection_name=collection_name):
            return False

        try:
            self.client.delete_vector(
                collection_name=collection_name,
                vector_id=vector_id
            )
            return True

        except Exception as e:
            self.logger.error(f"Error: {e}")
            return None