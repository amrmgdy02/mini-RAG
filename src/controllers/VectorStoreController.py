from itertools import count
from .BaseController import BaseController
from qdrant_client.models import Distance, VectorParams
from helpers.config import get_settings, Settings
from stores.VectorDB.providers.QdrantProvider import VectorDBProviderInterface
from stores.llms.providers.LLMProviderInterface import LLMInterface

import os
from typing import List

class VectorStoreController(BaseController):

    def __init__(self, embedding_model: LLMInterface, generation_llm: LLMInterface, vector_db_client: VectorDBProviderInterface):
        super().__init__()
        self.embedding_client = embedding_model
        self.vector_db_client = vector_db_client
        self.generation_llm = generation_llm
        self.settings = get_settings()

    def get_project_vectors_path(self, project_id: str):
        project_dir = os.path.join(
            self.vector_store_dir,
            project_id
        )

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir
    
    def embed_chunk(self, text: str, metadata: dict):
        
        project_id = metadata['project_id']
        if (len(text) == 0):
            return None
        
        embeddings = self.embedding_client.generate_embedding(
                        text=text,
                        document_type="query"
                    )
        
        if not self.vector_db_client.collection_exist(project_id):
            self.vector_db_client.create_collection(
                collection_name=project_id,
                vectors_config=VectorParams(
                    size=get_settings().EMBEDDING_SIZE, 
                    distance=Distance.DOT
                )
            )
        
        metadata['original_text'] = text  # Store the original chunk text in metadata
        
        self.vector_db_client.insert_vector(
            collection_name=project_id,
            vector=embeddings,
            metadata=metadata
        )
        
        return embeddings
    
    def search_similar_vectors(self, project_id: str, query_text: str, top_k: int=5):

        if not self.vector_db_client.collection_exist(project_id):
            raise ValueError(f"Collection for project_id {project_id} does not exist.")
        
        query_embedding = self.embedding_client.generate_embedding(
            text=query_text,
            document_type="query"
        )
        
        if not query_embedding:
            raise ValueError(f"Failed to generate embedding for query_text: {query_text}")

        results = self.vector_db_client.search(
            collection_name=project_id,
            query_vector=query_embedding,
            top_k=top_k
        )
        
        return results

    def answer_with_rag(self, query: str, project_id: str, chat_history: List[dict] = [], top_k: int = 5):
        print("Entered answer_with_rag")
        search_results = self.search_similar_vectors(
            project_id=project_id,
            query_text=query,
            top_k=top_k
        )
        print("Passed vector search")
        if not search_results or len(search_results) == 0:
            raise ValueError("No relevant documents found for the query.")
        
        context = "\n".join([f"### Content: {hit['payload'].get('original_text', '')}" for hit in search_results])
        print("Context: ", context)
        prompt = f"Use the following context to answer the question:\nContext: {context}\nQuestion: {query}\nAnswer:"
        print("Prompt: ", prompt)
        answer = self.generation_llm.generate_text(
            prompt=prompt,
            chat_history=chat_history,
            max_output_tokens=self.settings.DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
            temperature=self.settings.DEFAULT_GENERATION_TEMPERATURE
        )
        return answer
        return answer, search_results, chat_history + [{"role": "user", "content": query}, {"role": "assistant", "content": answer}]