import os
import httpx
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings

load_dotenv()

BASE_URL = os.getenv("OLLAMA_BASE_URL")
TOKEN = os.getenv("OLLAMA_TOKEN")

# Nagłówki autoryzacyjne
HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

def get_llm(model_role="coder", temperature=0.2):
    # Wybór modelu
    if model_role == "coder":
        model_name = os.getenv("MODEL_CODER", "qwen3-coder:30b")
    elif model_role == "pm":
        model_name = os.getenv("MODEL_PM", "llama3.3:70b")
    else:
        model_name = os.getenv("MODEL_CODER")

    print(f"🔌 LLM Factory: {model_name} (SSL VERIFY: FALSE)")

    # UWAGA: Tutaj jest kluczowa zmiana
    llm = ChatOllama(
        base_url=BASE_URL,
        model=model_name,
        temperature=temperature,
        # Wymuszamy timeout 120s i wyłączamy weryfikację SSL
        client_args={
            "headers": HEADERS,
            "verify": False,  # <--- TO MUSI BYĆ FALSE (typ bool), A NIE STRING Z .ENV
            "timeout": 120.0
        }
    )
    return llm

def get_embeddings():
    model_name = os.getenv("MODEL_EMBEDDING", "embeddinggemma:300m")
    
    embeddings = OllamaEmbeddings(
        base_url=BASE_URL,
        model=model_name,
        client_args={
            "headers": HEADERS,
            "verify": False, # <--- TU TEŻ NA SZTYWNO
            "timeout": 120.0
        }
    )
    return embeddings