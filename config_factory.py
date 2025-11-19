import os
import httpx
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings

# Ładowanie zmiennych z .env
load_dotenv()

# Pobieranie konfiguracji
BASE_URL = os.getenv("OLLAMA_BASE_URL")
TOKEN = os.getenv("OLLAMA_TOKEN")
VERIFY_SSL = os.getenv("OLLAMA_VERIFY_SSL", "True").lower() == "true"

# Przygotowanie nagłówków (Authorization)
HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# Przygotowanie klienta HTTP (obsługa SSL)
# To jest kluczowe dla Twojego środowiska korporacyjnego
http_client = httpx.Client(verify=VERIFY_SSL)

def get_llm(model_role="coder", temperature=0.2):
    """
    Zwraca skonfigurowaną instancję ChatOllama w zależności od roli.
    """
    # Wybór modelu na podstawie roli
    if model_role == "coder":
        model_name = os.getenv("MODEL_CODER", "qwen3-coder:30b")
    elif model_role == "pm":
        # Używamy llama3.3 lub innego 'mądrego' modelu do zarządzania
        model_name = os.getenv("MODEL_PM", "llama3.3:70b") 
    else:
        model_name = os.getenv("MODEL_CODER")

    print(f"🔌 Inicjalizacja LLM: {model_name} dla roli: {model_role}")

    llm = ChatOllama(
        base_url=BASE_URL,
        model=model_name,
        temperature=temperature,
        # Kluczowe dla Twojego setupu: przekazanie klienta i nagłówków
        client_args={
            "headers": HEADERS,
            "verify": VERIFY_SSL # Przekazujemy verify=False jeśli tak jest w .env
        }
    )
    return llm

def get_embeddings():
    """
    Zwraca skonfigurowaną instancję do Embeddingów (dla RAG).
    """
    model_name = os.getenv("MODEL_EMBEDDING", "embeddinggemma:300m")
    
    embeddings = OllamaEmbeddings(
        base_url=BASE_URL,
        model=model_name,
        client_args={
            "headers": HEADERS,
            "verify": VERIFY_SSL
        }
    )
    return embeddings