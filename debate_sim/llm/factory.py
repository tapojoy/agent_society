from llm.providers.ollama_provider import OllamaProvider

from config import BASE_URL, API_KEY

def get_provider():

    return OllamaProvider(
        base_url=BASE_URL,
        api_key=API_KEY
    )