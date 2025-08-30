from .providers.QdrantProvider import QdrantProvider
from controllers.VectorStoreController import VectorStoreController, BaseController

class VectorDBFactory():
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        vector_db_path = BaseController().vector_store_dir

        if provider == "QDRANT":
            return QdrantProvider(db_path=vector_db_path)
        
        else:
            return None