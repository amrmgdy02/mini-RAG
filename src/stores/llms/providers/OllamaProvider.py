from .LLMProviderInterface import LLMInterface
import requests
import logging
import json

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
        
        self.system_message = "\n".join([
                "You are a helpful assistant to generate a response for the user.",
                "You will be provided by a set of documents that supposed to be relevant to the user's query.",
                "You have to generate a response based on the documents provided.",
                "Ignore the documents that are not relevant to the user's query.",
                "You have to generate response in the same language as the user's query.",
                "Be polite and respectful to the user.",
                "Be precise and concise in your response. Avoid unnecessary information.",
                "If you can't get the answer from the documents, you can apologize to the user.",
            ])
        
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
        print("Entered Generate Text")
        if not self.generation_model_name:
            raise ValueError("Generation model is not set.")

        valid_prompt = prompt[:self.default_input_max_characters] if len(prompt) > self.default_input_max_characters else prompt

        chat_history = [{"role": "system", "content": self.system_message}] + chat_history if chat_history else [{"role": "system", "content": self.system_message}]

        messages = chat_history + [{"role": "user", "content": valid_prompt}]
        print("Messages: ", messages)
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.generation_model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature or self.default_generation_temperature,
                    "num_predict": max_output_tokens or self.default_generation_max_output_tokens
                }
            }
        )
        print("Response: ", response)
        if response.status_code != 200:
            self.logger.error(f"Error from Ollama: {response.text}")
            return None
            
        try:
            # Parse only the first JSON object if multiple are present
            first_json = json.loads(response.text.splitlines()[0])
            print("Response: ", first_json["message"]["content"])
            return first_json["message"]["content"]
        except Exception as e:
            self.logger.error(f"Error parsing Ollama response: {e}")
            return None
    
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