import os
from langgraph.graph import StateGraph, END
from core.state import AgentState

# Importy agentów
from agents.pm_agent import pm_node
from agents.architect_agent import architect_node
from agents.coder_agent import coder_node

# --- FUNKCJE POMOCNICZE DLA APLIKACJI WEBOWEJ ---

def save_files(project_name, files):
    """
    Zapisuje wygenerowane pliki na dysk w folderze workspace.
    """
    base_path = os.path.join("workspace", project_name)
    
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        
    print(f"\n💾 Zapisuję projekt w: {base_path}")
    
    saved_paths = []
    for file_data in files:
        file_name = file_data.get("name")
        content = file_data.get("content")
        
        # Obsługa podkatalogów (np. src/main.py)
        full_path = os.path.join(base_path, file_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"   -> Utworzono: {file_name}")
            
    return base_path

def generate_project(user_prompt):
    """
    Główna logika: Tworzy graf, uruchamia agentów i zwraca listę plików.
    """
    # 1. Budowa grafu
    workflow = StateGraph(AgentState)
    
    workflow.add_node("product_manager", pm_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", coder_node)
    
    workflow.set_entry_point("product_manager")
    workflow.add_edge("product_manager", "architect")
    workflow.add_edge("architect", "developer")
    workflow.add_edge("developer", END)
    
    app = workflow.compile()
    
    initial_state = {
        "requirements": user_prompt,
        "plan": [],
        "file_structure": [],
        "project_files": [],
        "messages": [],
        "iteration_count": 0
    }
    
    print(f"🚀 Rozpoczynam generowanie projektu: {user_prompt[:50]}...")
    
    try:
        # Uruchamiamy graf (z limitem kroków dla bezpieczeństwa)
        result = app.invoke(initial_state, {"recursion_limit": 50})
        
        # Zwracamy tylko listę plików do aplikacji webowej
        return result.get("project_files", [])
        
    except Exception as e:
        print(f"❌ Błąd w trakcie pracy agentów: {e}")
        return {"error": str(e)}

# --- TRYB TESTOWY (CLI) ---
if __name__ == "__main__":
    print("--- TRYB KONSOLOWY (TEST) ---")
    print("Aby uruchomić interfejs webowy, wpisz: streamlit run app.py")
    
    prompt = input("\nPodaj opis projektu: ")
    if prompt.strip():
        files = generate_project(prompt)
        
        if isinstance(files, list) and files:
            # Używamy nazwy 'test_project' dla testów konsolowych
            save_files("test_project", files)
            print("\n✅ Gotowe! Sprawdź folder workspace/test_project")
        else:
            print("\n⚠️ Nie udało się wygenerować plików lub wystąpił błąd.")