from litellm import completion, embedding
from config import get_api_keys

class LitellmEmbeddings:
    def __init__(self, model, api_key, api_base=None, api_version=None):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.api_version = api_version

    def embed_documents(self, texts):
        endpoint = None
        if self.model.startswith("azure/"):
            endpoint = f"{self.api_base}/{self.api_version}/embeddings"
        
        response = embedding(model=self.model, input=texts, api_key=self.api_key, api_base=self.api_base, api_version=self.api_version)
        embeddings = [item['embedding'] for item in response['data']]
        return embeddings

    def embed_query(self, query):
        endpoint = None
        if self.model.startswith("azure/"):
            endpoint = f"{self.api_base}/{self.api_version}/embeddings"
        
        response = embedding(model=self.model, input=[query], api_key=self.api_key, api_base=self.api_base, api_version=self.api_version)
        embedding_result = response['data'][0]['embedding']
        return embedding_result

def create_litellm_client(model):
    # Just validate the model once, get API keys
    api_key = get_api_keys(model)
    return completion

def create_litellm_client_embeddings(model, api_key, api_base=None, api_version=None):
    return LitellmEmbeddings(model, api_key, api_base, api_version)