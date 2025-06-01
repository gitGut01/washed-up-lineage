import os
import pickle
from langchain_google_vertexai import ChatVertexAI
from langchain_ollama.llms import OllamaLLM

# Google Vertex AI Configuration
GEMINI_TOKEN_PICKLE_PATH='token.pickle'
GEMINI_MODEL='gemini-1.5-pro-001'
GEMINI_PROJECT='your-gcp-project'

# Ollama Configuration
OLLAMA_MODEL='llama3.2:3b-instruct-q4_K_M'

class LLMClient:
    def __init__(self):
        self.scopes = [
            "https://www.googleapis.com/auth/cloud-platform"
        ]

    def authorize_google(self):
        credentials = None
        token_file = GEMINI_TOKEN_PICKLE_PATH

        if os.path.exists(token_file):
            with open(token_file, "rb") as token:
                credentials = pickle.load(token)

        self.credentials = credentials
        return credentials

    def get_vertex_model(self):
        credentials = self.authorize_google()
        return ChatVertexAI(
            model=GEMINI_MODEL,
            temperature=0,
            max_tokens=None,
            max_retries=6,
            stop=None,
            project=GEMINI_PROJECT,
            credentials=credentials,
        )

    def get_ollama_model(self):
        return OllamaLLM(model=OLLAMA_MODEL, temperature=0)

    def get_model(self):
        # Replace this with the get_<model_name>_model() function you want to use
        return self.get_ollama_model()