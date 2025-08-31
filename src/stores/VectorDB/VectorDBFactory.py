from .providers.QdrantProvider import QdrantProvider
from controllers.VectorStoreController import VectorStoreController, BaseController

class VectorDBFactory():
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):

        if provider == "QDRANT":
            return QdrantProvider()
        
        else:
            return None