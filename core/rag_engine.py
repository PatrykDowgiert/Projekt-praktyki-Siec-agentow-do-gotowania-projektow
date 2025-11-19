import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from config_factory import get_embeddings  # Importujemy naszą bezpieczną fabrykę!

DB_PATH = "./chroma_db_store"

class ProjectKnowledgeBase:
    def __init__(self):
        # Pobieramy embeddingi skonfigurowane pod Twoją Ollamę (SSL/Auth)
        self.embedding_function = get_embeddings()
        
        # Inicjalizacja ChromaDB
        self.vector_store = Chroma(
            persist_directory=DB_PATH,
            embedding_function=self.embedding_function
        )
        
    def ingest_document(self, file_path: str):
        """Wczytuje plik i zapisuje w bazie wektorowej"""
        if not os.path.exists(file_path):
            print(f"❌ Nie znaleziono pliku: {file_path}")
            return

        print(f"📥 Przetwarzanie: {file_path}")
        
        # Wybór loadera
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding="utf-8")
            
        docs = loader.load()
        
        # Dzielenie na kawałki (Chunking)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(docs)
        
        # Zapis do bazy
        if chunks:
            self.vector_store.add_documents(chunks)
            print(f"✅ Zindeksowano {len(chunks)} fragmentów w ChromaDB.")
        
    def search(self, query: str, k=3):
        """Szuka w bazie wiedzy"""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        results = retriever.invoke(query)
        return results

    def clear(self):
        """Czyści bazę (przydatne przy restarcie projektu)"""
        if os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)
            print("🧹 Baza wektorowa wyczyszczona.")