from .LLMProviderInterface import LLMInterface
import requests
import logging

class OllamaProvider(LLMInterface):
    
    def __init__(self, base_url: str = "http://172.18.32.1:11434",
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):
        
        self.base_url = base_url
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        
        self.generation_model_name = None
        self.embedding_model_name = None
        self.embedding_size = None
        
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_id: str):
        self.generation_model_name = model_id
        self.logger.info(f"Generation model set to: {model_id}")

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_name = model_id
        self.embedding_size = embedding_size
        self.logger.info(f"Embedding model set to: {model_id}")

    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                      temperature: float = None):
        if not self.generation_model_name:
            raise ValueError("Generation model is not set.")
        
        valid_prompt = prompt[:self.default_input_max_characters] if len(prompt)>self.default_input_max_characters else prompt
        
        messages = chat_history + [{"role": "user", "content": valid_prompt}]
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.generation_model_name,
                "messages": messages,
                "options": {
                    "temperature": temperature or self.default_generation_temperature,
                    "num_predict": max_output_tokens or self.default_generation_max_output_tokens
                }
            }
        )
        
        if response.status_code != 200:
            self.logger.error(f"Error from Ollama: {response.text}")
            return None
            
        return response.json()["message"]["content"]
    
    def generate_embedding(self, text: str, document_type: str = None):
        if not self.embedding_model_name:
            raise ValueError("Embedding model is not set.")
        
        input = text[:self.default_input_max_characters] if len(text)>self.default_input_max_characters else text
        
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={
                "model": self.embedding_model_name,
                "prompt": input
            }
        )
        if response.status_code != 200:
            self.logger.error(f"Error generating embedding: {response.text}")
            return None
            
        return response.json()["embedding"]