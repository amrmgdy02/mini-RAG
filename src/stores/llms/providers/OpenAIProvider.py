from .LLMProviderInterface import LLMInterface
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):
    
    def __init__(self, api_key: str, api_url: str=None,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key = self.api_key,
            api_url = self.api_url
        )

        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_id: str):
        """
        Set the model to be used for text generation.
        """
        self.generation_model_id = model_id
        self.logger.info(f"Generation model set to: {model_id}")
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """
        Set the model and size for text embedding.
        """
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.logger.info(f"Embedding model set to: {model_id} with size: {embedding_size}")
        
    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                      temperature: float = None):
        """
        Generate text based on the provided prompt and chat history.
        """
        if not self.generation_model_id:
            raise ValueError("Generation model is not set.")
        
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history + [{"role": "user", "content": prompt[:self.default_input_max_characters]}],
            max_tokens=max_output_tokens or self.default_generation_max_output_tokens,
            temperature=temperature or self.default_generation_temperature
        )
        
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        return response.choices[0].message['content']
    
    def generate_embedding(self, text: str, document_type: str = None):
        """
        Generate an embedding for the provided text.
        """
        if not self.embedding_model_id or not self.embedding_size:
            raise ValueError("Embedding model is not set.")
        
        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=text[:self.default_input_max_characters]
        )
        
        if not response or not response.data or len(response.data) == 0:
            self.logger.error("Error while generating embedding with OpenAI")
            return None
        
        return response.data[0].embedding