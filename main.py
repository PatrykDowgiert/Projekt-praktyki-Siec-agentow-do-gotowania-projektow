import os
from langgraph.graph import StateGraph, END
from core.state import AgentState

# Importy agentów
from agents.pm_agent import pm_node
from agents.architect_agent import architect_node
from agents.coder_agent import coder_node
from agents.qa_agent import qa_node  # Upewnij się, że masz qa_agent.py

# --- FUNKCJE POMOCNICZE (Obsługa plików) ---

def save_files_to_disk(project_name, files):
    """
    Zapisuje listę plików na dysk.
    Używana przez app.py.
    """
    base_path = os.path.join("workspace", project_name)
    
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        
    print(f"\n💾 Zapisuję projekt w: {base_path}")
    
    for file_data in files:
        file_name = file_data.get("name")
        content = file_data.get("content")
        
        # Obsługa podkatalogów
        full_path = os.path.join(base_path, file_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"   -> Utworzono: {file_name}")
            
    return base_path

# --- LOGIKA DECYZYJNA (ROUTER) ---

def route_after_qa(state: AgentState):
    """
    Decyduje co robić po sprawdzeniu kodu przez QA.
    """
    feedback = state.get("test_feedback", "")
    structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    
    # 1. Jeśli QA znalazł błąd -> WRACAMY do Codera poprawić ten sam plik
    if "FAILED" in feedback:
        print("   -> 🔙 Wykryto błąd składni. Powrót do Programisty.")
        return "developer"
    
    # 2. Jeśli jest OK -> Sprawdzamy czy są kolejne pliki do napisania
    if idx < len(structure):
        return "developer" # Idziemy pisać następny plik
    else:
        return "end" # Wszystkie pliki gotowe

# --- GŁÓWNA FUNKCJA SILNIKA ---

def run_project_agent(user_prompt, previous_state=None):
    """
    Główna funkcja uruchamiana przez Streamlit (app.py).
    Tworzy graf, zarządza pamięcią i uruchamia agentów.
    """
    # 1. Definicja Grafu
    workflow = StateGraph(AgentState)