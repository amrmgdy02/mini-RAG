from .providers.OpenAIProvider import OpenAIProvider
from .providers.OllamaProvider import OllamaProvider

class LLMFactory():
    def __init__(self, config: dict):
        self.config = config
        
    def create(self, provider: str):
        
        if provider == "OPENAI":
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max_characters=self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.config.DEFAULT_GENERATION_TEMPERATURE,
            )
        
        elif provider == "OLLAMA":
            return OllamaProvider(
                base_url=self.config.OLLAMA_BASE_URL, 
                default_input_max_characters=self.config.DEFAULT_INPUT_MAX_CHARACTERS, 
                default_generation_max_output_tokens=self.config.DEFAULT_GENERATION_MAX_OUTPUT_TOKENS, 
                default_generation_temperature=self.config.DEFAULT_GENERATION_TEMPERATURE
            )
        
        else:
            return None