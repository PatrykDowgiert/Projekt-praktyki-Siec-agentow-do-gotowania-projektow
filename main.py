# ==========================================
# ☢️ OPCJA NUKLEARNA: GLOBALNE WYŁĄCZENIE SSL
# ==========================================
import ssl
import os
import warnings

warnings.filterwarnings("ignore")
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
# ==========================================

from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.pm_agent import pm_node
from agents.architect_agent import architect_node
from agents.coder_agent import coder_node
# Na razie pomijamy QA dla uproszczenia generowania wielu plików, 
# ale można go dodać później jako weryfikatora JSONa.

def save_project_to_disk(project_name, files):
    """Funkcja zapisująca wygenerowane pliki na dysk"""
    base_path = os.path.join("workspace", project_name)
    
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        
    print(f"\n💾 Zapisuję projekt w: {base_path}")
    
    for file_data in files:
        file_name = file_data.get("name")
        content = file_data.get("content")
        
        # Obsługa podkatalogów (np. src/main.py)
        full_path = os.path.join(base_path, file_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"   -> Utworzono: {file_name}")

def run_interactive_mode():
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
    
    print("\n🤖 --- AGILE DEV AGENTS (Project Generator) ---")
    print("Wpisz opis projektu, który chcesz stworzyć (lub 'exit').")
    
    while True:
        user_input = input("\n>>> Twój pomysł: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        if not user_input.strip():
            continue
            
        # Nazwa projektu do folderu (proste czyszczenie nazwy)
        project_name = user_input.split()[0:3] # Pierwsze 3 słowa
        project_name = "_".join(project_name).replace(" ", "_").lower()
        
        initial_state = {
            "requirements": user_input,
            "plan": [],
            "file_structure": [],
            "project_files": [],
            "messages": []
        }
        
        print(f"🚀 Rozpoczynam pracę nad: {project_name}...")
        
        try:
            # Zwiększamy recursion_limit, bo generowanie wielu plików trwa
            result = app.invoke(initial_state, {"recursion_limit": 50})
            
            files = result.get("project_files", [])
            
            if files:
                save_project_to_disk(project_name, files)
                print(f"\n✅ Gotowe! Sprawdź folder workspace/{project_name}")
            else:
                print("\n⚠️ Coś poszło nie tak - programista nie zwrócił plików.")
                
        except Exception as e:
            print(f"\n❌ Błąd: {e}")

if __name__ == "__main__":
    run_interactive_mode()